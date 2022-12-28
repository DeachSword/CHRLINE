import re, setuptools

with open('CHRLINE/__init__.py') as f:
    version = re.search(r'__version__\s*=\s*\"(.+?)\"', f.read()).group(1)
    
with open("README.md","r", encoding="utf-8") as f:
  long_description = f.read()

setuptools.setup(
  name="CHRLINE",
  version=version,
  author="DeachSword",
  description="LINE API!",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/DeachSword/CHRLINE",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3.6"
  ],
  install_requires=[
    'pycryptodome==3.9.8', # ez:D
    'xxhash',
    'rsa',
    'requests',
    'python-axolotl-curve25519',
    'httpx[http2]',
    'h2>=3.2.0',
    'gevent',
    'cryptography',
    'thrift',
    'qrcode',
    'Image',
  ]
)