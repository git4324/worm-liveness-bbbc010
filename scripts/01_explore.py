"""Print what is in data/ so filenames, channels and mask pairing can be confirmed."""
import pathlib, collections
import tifffile

root = pathlib.Path("data")
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    files = sorted(f for f in d.rglob("*") if f.is_file())
    exts = collections.Counter(f.suffix.lower() for f in files)
    print(f"\n{d.name}: {len(files)} files {dict(exts)}")
    for f in files[:6]:
        print("  ", f.relative_to(d))

imgs = sorted(root.glob("*images*/**/*.tif*"))
if imgs:
    a = tifffile.imread(imgs[0])
    print("\nfirst image:", imgs[0].name, a.shape, a.dtype, "min", a.min(), "max", a.max())
    print("total images found:", len(imgs))
