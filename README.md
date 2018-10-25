# Setup on `dev`

Install Miniconda in your `$PATH`:
```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
```

Create the dr1ven conda environment:
```
conda create -n dr1ven python=3.6
```

Install pytorch and other dependencies:
```
conda install pytorch torchvision cuda92 -c pytorch
pip install -r requirements.txt
```
