
for i in {0..9..1}  
do  
python main_ours.py --backbone resnet34 --seed $i

python main_ours.py --backbone resnet50 --seed $i

done



