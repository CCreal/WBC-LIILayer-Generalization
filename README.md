# Improved Generalization of White Blood Cell Classification by Learnable Illumination Intensity Invariant Layer

## Dataset
- RaabinWBC
	- Download and decompress `Train`, `TestA`, and `TestB` into `./data/RaabinWBC/` from https://raabindata.com/free-data/.
- LISC
	- Download and decompress `LISC` into `./data/` from https://drive.google.com/file/d/1gknVrSs1CRy8PoIh1HXiGu-1ObH3cQ9S, which is provided by https://github.com/nimaadmed/WBC_Feature. 
	- then `python3 scripts/organize_lisc.py`, which will make `./data/LISCCropped`

## Environment

	```
	cd env
	conda env create -f environment.yaml
	conda activate wbc
	```

## Usage
- Train backbones without LII-Layer:
	- `bash train_wo_iii.sh`
- Train backbones with LII-Layer:
	- `bash train_add_iii.sh`
- Test backbones without LII-Layer:
	```
    python main.py \
    --backbone resnet50 \ # or resnet34
    --seed 0 \ # or 1,...,9
    --epoch 0 \
    --test-img-root ./data/RaabinWBC/TestA \ # or ./data/RaabinWBC/Test-B or ./data/LISCCropped
    --saveroot ./experiments/default_test/TestA \ # your path to save results
    --resume ./experiments/yourpath/model_99.pth # path model saved

	```
- Test backbones with LII-Layer:
	```
    python main_ours.py \
    --backbone resnet50 \ # or resnet34
    --seed 0 \ # or 1,...,9
    --epoch 0 \
    --test-img-root ./data/RaabinWBC/TestA \ # or ./data/RaabinWBC/Test-B or ./data/LISCCropped
    --saveroot ./experiments/default_test/TestA \ # your path to save results
    --resume ./experiments/yourpath/model_99.pth # path model saved

	```

