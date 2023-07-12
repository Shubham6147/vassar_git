import rasterio as rio
import os
import glob

def process_metadata ( fname ):
    """A function to extract the relelvant metadata from the
    USGS control file. Returns dicionaries with LMAX, LMIN,
    QCAL_LMIN and QCAL_LMAX for each of the bands of interest."""

    fp = open( fname, 'r') # Open metadata file
    gain = {}
    bias = {}
    K1 = {}
    K2 = {}


    for line in fp: #
      # Check for LMAX and LMIN strings
      # Note that parse logic is identical to the first case
      # This version of the code works, but is rather inelegant!
      if ( line.find ("RADIANCE_MULT_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [10,11]: # Is this one of the bands we want?
              gain[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("RADIANCE_ADD_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [10,11]: # Is this one of the bands we want?
              bias[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("K1_CONSTANT_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [10,11]: # Is this one of the bands we want?
              K1[the_band] = float ( s[-1] ) # Get constant as float
      elif ( line.find ("K2_CONSTANT_BAND") >= 0 ):
          s = line.split("=") # Split by equal sign
          the_band = int(s[0].split("_")[3]) # Band number as integer
          if the_band in [10,11]: # Is this one of the bands we want?
              K2[the_band] = float ( s[-1] ) # Get constant as float

    return ( bias, gain, K1, K2 )


def DN_to_radiance(DN_band, bias, gain):
    print ("RADIANCE_MULT_BAND : " + str(gain))
    print ("RADIANCE_ADD_BAND : " + str(bias))
    #rst = arcpy.Raster(DN_band)

    rst = rio.open(DN_band).read(0)


    Radiance = (gain * rst + bias)

    return Radiance

#================= For LST Estimation =====================
def Radiance_to_Brightness_temperature(Radiance_band, K1, K2):
    rst = Radiance_band
    BT = (K2 / (Ln(K1/rst+1)))

    return BT

def Emissivity_cor_LST(surface_emissivity, Brightness_temp):
    Sur_emis = surface_emissivity
    BT = Brightness_temp
    Roh = float(0.01438)                # Roh = h*(c/o);
                                        # Where, h = plank constant (6.626 * 10^-34 Js;)
                                        # c = Velocity of light (2.998*10^8 m/s;
                                        # o = Boltzmann constant (1.38 * 10^-23 J/K)
    Lambda = float(0.00115)             #wavelength of emitted radiance (for which the peak response and the
                                        #average of the limiting wavelength (lambda =11.5 micrometer)) will be used

    LST = (BT / (1 + (((Lambda*BT)/Roh))*Ln(float(Sur_emis/10000))))

    return LST



def Split_window_LST_EQ11 (THR_CH10, THR_CH11, Emissivity_ch10, Emissivity_ch11, bias10, gain10, bias11, gain11, K1_10, K2_10, K1_11, K2_11, w):

    print("Calculating DN to Radiance for thermal band")
    DnToRad_CH10 = DN_to_radiance(THR_CH10, bias10, gain10)
    DnToRad_CH11 = DN_to_radiance(THR_CH11, bias11, gain11)

    print("Calculating Brightness temperature")
    BT_CH10 = Radiance_to_Brightness_temperature (DnToRad_CH10, K1_10, K2_10)
    BT_CH11 = Radiance_to_Brightness_temperature (DnToRad_CH11, K1_11, K2_11)

    Delta_E = (float(Emissivity_ch10 - Emissivity_ch11))/10000.0
    Avg_E = float((Emissivity_ch10 + Emissivity_ch11) / 2.0)/10000.0
    T10 = BT_CH10
    T11 = BT_CH11
    W = w
    LST = (T10 +(1.378 *(T10-T11)) + (0.183*(T10-T11))*2-0.268 + (54.3-(2.238 *W)*(1-Avg_E) + ((16.4 *W)-129.2)*Delta_E))



def Split_window_LST_EQ12 (THR_CH10, THR_CH11, Emissivity_ch10, Emissivity_ch11, bias10, gain10, bias11, gain11, K1_10, K2_10, K1_11, K2_11):

    print ("Calculating DN to Radiance for thermal band")
    DnToRad_CH10 = DN_to_radiance(THR_CH10, bias10, gain10)
    DnToRad_CH11 = DN_to_radiance(THR_CH11, bias11, gain11)

    print ("Calculating Brightness temperature")
    BT_CH10 = Radiance_to_Brightness_temperature (DnToRad_CH10, K1_10, K2_10)
    BT_CH11 = Radiance_to_Brightness_temperature (DnToRad_CH11, K1_11, K2_11)
    Delta_BT = BT_CH10 - BT_CH11
    Avg_BT = (BT_CH10 + BT_CH11)/2.0

    Delta_E = (Emissivity_ch10 - Emissivity_ch11)/ 10000.0
    Avg_E = ((Emissivity_ch10 + Emissivity_ch11) / 2.0)/10000.0

    T10 = BT_CH10
    T11 = BT_CH11
    b0 = -0.41165
    b1 = 1.00522
    b2 = 0.14543
    b3 = -0.27297
    b4 = 4.06655
    b5 = -6.92512
    b6 = -18.27461
    b7 = 0.24468

    LST = (b0 + (b1 + b2 * ((1 - Avg_E) / Avg_E) + b3 * (Delta_E / (Avg_E ** 2))) *Avg_BT + (b4 + b5 * ((1 - Avg_E) / Avg_E) + b6 * (Delta_E / (Avg_E ** 2))) * (Delta_BT / 2) + b7 * (Delta_BT) ** 2)

    return LST


def findfiles(root_dir):
    toprocess = []  # list to store paths for processing in
    for root,dir,files in os.walk(root_dir):
        for name in files:
            if fnmatch.fnmatch(name, '*MTL.txt'):
               toprocess.append( os.path.join(root, name) )
               #print os.path.join(root, name)
    return toprocess



file_list = [r"D:\LST_Test\LC08_L1TP_144048_20230527_20230603_02_T1\LC08_L1TP_144048_20230527_20230603_02_T1_MTL.txt"]


for mtl_file in file_list:
    print ("Processing started: " + mtl_file)
    metadata_file = mtl_file
    (bias, gain, K1, K2 ) = process_metadata (metadata_file)
    original_fname = os.path.basename (metadata_file)
    prefix = mtl_file[:-8]             #original_fname.split("_")[0]
    fname_prefix = os.path.join ( os.path.dirname (metadata_file), prefix )
    TIR_CH10 = fname_prefix + "_B10.TIF"
    TIR_CH11 = fname_prefix + "_B11.TIF"
    Emissivity_CH10 = fname_prefix + "_Emiss1011.TIF\EmissCH10"
    print(Emissivity_CH10)
    Emissivity_CH11 = fname_prefix + "_Emiss1011.TIF\EmissCH11"
    outfile_name = fname_prefix + "SW_EQ12_LST.tif"
    print("=========")
    print("Processing of " + os.path.basename(outfile_name) + " started for LST calculation")

    LST_cal = Split_window_LST_EQ12(TIR_CH10, TIR_CH11, Emissivity_CH10, Emissivity_CH11, bias[10], gain[10], bias[11], gain[11], K1[10], K2[10], K1[11], K2[11])


    #LST_cal.save(outfile_name)
    print ("LST calculation of " + os.path.basename(outfile_name) + " is Finished")


