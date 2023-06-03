import os

directory_list = list()
for root, dirs, files in os.walk("../../experiments/parameters/ADPSO-ES-0/RLS", topdown=False):
    for name in dirs:
        directory_list.append(float(os.path.join(name)))

directory_list.sort()

print (directory_list)
