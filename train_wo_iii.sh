
for i in {0..9..1}  
do  
python main.py --backbone resnet50 --seed $i
done


for i in {0..9..1}  
do  
python main.py --backbone resnet34 --seed $i
done