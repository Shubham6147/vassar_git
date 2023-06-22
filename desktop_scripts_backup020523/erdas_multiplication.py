import os 
#projects = ["annapurna", "indiramma", "ranganayaka", "lmd", "ns", "srsp", "syp", "singur", "mallanna"]
projects = [ "lmd", "srsp"]

lines = []

for season in ["dry", "wet"]:
    for project in projects:
        for i in range(0,17):
            outfile = f"E:/ET_calculation/multiplication_nrsc/2020_21/{project}_2020_2021_year_ndvi_mask_{season}_{i}_et.tif"
            if not os.path.exists(outfile):
                lines.append(f'modeler -nq e:/et_calculation/ndvi_cor/multiplication/multiplication.mdl -meter -state "e:/et_calculation/ndvi_cor/done/{project}_2020_2021_year_ndvi_mask_{season}_cor_85_{i}_interpolated_kc.tif" "e:/et_calculation/nrsc_et0/stack_2021/{i+1}.tif" "e:/et_calculation/multiplication_nrsc/2020_21/{project}_2020_2021_year_ndvi_mask_{season}_{i}_et.tif"')

    #break





with open('2021_erdas_processing_multiplication_batch_nrsc.txt', 'w') as f:
    for line in lines:
        f.write(line)
        f.write('\n')
