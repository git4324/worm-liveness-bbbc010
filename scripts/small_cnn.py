"""A small two-channel convolutional model that runs on a CPU."""
import numpy as np
import torch
from skimage.transform import resize
from torch import nn

from study import image_pairs, read_image

EPOCHS = 16
BATCH_SIZE = 16


def load_pixels(wells):
    paired = list(image_pairs())
    assert [row.well for row, *_ in paired] == list(wells)
    images = []
    for _, bf, fluorescence, _ in paired:
        channels = []
        for path in (bf, fluorescence):
            raw = read_image(path).astype(np.float32)
            low, high = np.percentile(raw, [1, 99])
            scaled = np.clip((raw - low) / max(high - low, 1), 0, 1)
            channels.append(resize(scaled, (96, 128), anti_aliasing=True))
        images.append(channels)
    return torch.from_numpy(np.asarray(images, dtype=np.float32))


def architecture():
    # Pool spatial locations before prediction to reduce the number of weights.
    return nn.Sequential(
        nn.Conv2d(2, 8, 5, stride=2, padding=2), nn.BatchNorm2d(8), nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(8, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(16, 24, 3, padding=1), nn.BatchNorm2d(24), nn.ReLU(),
        nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(24, 1),
    )


def predict(pixels, train, test, train_targets, seed):
    # Fit a fresh model in each fold, with CPU-only deterministic operations.
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(seed)
    net = architecture()
    loss_fn = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.003)
    targets = torch.as_tensor(train_targets, dtype=torch.float32)
    for _ in range(EPOCHS):
        for batch in torch.randperm(len(train)).split(BATCH_SIZE):
            batch_images = pixels[train[batch.numpy()]]
            logits = net(batch_images).squeeze(1)
            loss = loss_fn(logits, targets[batch])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    net.eval()
    with torch.no_grad():
        return net(pixels[test]).squeeze(1).sigmoid().numpy()
