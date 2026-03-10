import os
import glob
data_dir = '/home/nikhil.repala/BRSM/Project/BRSM data csv/BRSM data csv/'
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

total_ab = 0
total_nb = 0

for file in csv_files:
    fname = os.path.basename(file).lower()
    if 'ab' in fname:
        total_ab += 1
    elif 'nb' in fname:
        total_nb += 1

print(f"Before: AB={total_ab}, NB={total_nb}, Total={len(csv_files)}")

