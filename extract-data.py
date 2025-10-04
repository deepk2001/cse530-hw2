import os
import subprocess
from time import sleep

out_file_path = 'cacti/out.txt'
config_file_path = 'cacti/cache.cfg'
experiment_1_saved_data_file_path = 'experiment_1_saved_data.txt'
experiment_2_saved_data_file_path = 'experiment_2_saved_data.txt'


def update_cache_cfg(parameter, value ): 
    with open(config_file_path, "r") as f:
        lines = f.readlines()
    
    if parameter == "size":
        for i, line in enumerate(lines):
            if  line.strip().startswith("-size (bytes)"):
                lines[i] = f"-size (bytes) {value}\n"
                break
    elif parameter == "associativity":
        for i, line in enumerate(lines):
            if  line.strip().startswith("-associativity"):
                lines[i] = f"-associativity {value}\n"
                break
    else:
        print(f"Invalid parameter: {parameter}")
        return
    with open(config_file_path, "w") as f:
        f.writelines(lines)
    return

def extract_data(out_file_path, search_strings, extracted_data):
    try:
        with open(out_file_path, 'r') as f:
            for line in f:
                for search_string in search_strings:
                    if search_string in line:
                        lineStr = line.strip()     
                        print(lineStr)       
                        extracted_data[search_string].append(float(lineStr.split(search_string)[1]))
                        break  
    except FileNotFoundError:
        print(f'Error: The file at {out_file_path} was not found.')

def store_experiment_data(experiment_data_store, extracted_data):
    mode = "a" if not os.path.exists(experiment_data_store) else "w"
    with open(experiment_data_store, mode) as f:
        for key, values in extracted_data.items():
            # Convert all values to strings and join with commas
            line = ",".join([str(v) for v in values])
            # Prepend key
            line = f"{key},{line}\n"
            f.write(line)
    return

def clear_out_file():
    if os.path.exists(out_file_path):
        open(out_file_path, "w").close()
        print(f"{out_file_path} has been cleared.")

def perform_experiment1(size_min,size_max, size_step):
    search_strings = ['Data array: Area (mm2):','Total dynamic read energy per access (nJ):','Access time (ns):']
    update_cache_cfg("associativity", 4) # set associativity to 4 for experiment 1
    extracted_data = {"cache_size":[]}
    for i in search_strings:
        extracted_data[i] = []

        
    for i in range(size_min, size_max + 1, size_step):
        clear_out_file()
        cache_size_in_bytes = i * 1024
        update_cache_cfg("size", cache_size_in_bytes)
        extracted_data["cache_size"].append(cache_size_in_bytes)
        command = "cd cacti; ./cacti -infile cache.cfg >> out.txt; cd -"
        subprocess.run(command, shell=True)
        extract_data(out_file_path, search_strings, extracted_data)
    store_experiment_data(experiment_1_saved_data_file_path,extracted_data)
    return

def perform_experiment2(associativity_min,associativity_max):
    search_strings = ['Data array: Area (mm2):','Total dynamic read energy per access (nJ):','Access time (ns):']
    update_cache_cfg("size", 512*1024) # cache size at 512Kb for experiment 2
    extracted_data = {"associativity":[]}
    for i in search_strings:
        extracted_data[i] = []

    i=associativity_min
    while (i <= associativity_max):
        clear_out_file()
        update_cache_cfg("associativity", i)
        extracted_data["associativity"].append(i)
        command = "cd cacti; ./cacti -infile cache.cfg >> out.txt; cd -"
        subprocess.run(command, shell=True)
        extract_data(out_file_path, search_strings, extracted_data)
        i*=2
    store_experiment_data(experiment_2_saved_data_file_path,extracted_data)
    return

perform_experiment1(64,2048, 64)
perform_experiment2(2,16)

