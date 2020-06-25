import os
import subprocess

def interaction_window():
    welcome_response = input("Hello! Welcome to the rav1e benchmarking tool, \
used to test different characteristics of performance of the rav1e codec. \
Would you like to continue (Y/N)? ")
    if welcome_response in ("Y","y","yes","Yes"):
        convert_and_encode()
    elif welcome_response in ("N","n","no","No"):
        quit()
    else:
        print("please enter Y or N")
        interaction_window()

def convert_and_encode():
    rav_dir = input("Enter absolute file path for the rav1e directory (ex: if the file is in a folder called \"rav-full\", write \"rav-full/rav1e/\"): ")
    vids_dir = input("Enter the absolute directory path for where the .y4m videos are stored (ex: if in a folder called \"in_vids\" in the Downloads directory, write \"Downloads/in_vids/\"): ")
    output_vids_dir = input("Enter the absolute directory path for where the .ivf videos will be saved (ex: if in the Downloads directory, write \"Downloads/\"): ")
    if input("are you testing?") == "y":
        rav_dir = "rav-full/rav1e/"
        vids_dir = "Downloads/in_vids/"
        output_vids_dir = "Downloads/out_vids/"
    vids_dir_path = os.fsencode(vids_dir)
    if str(input("skip to analysis?"))== "y":
        get_stats(vids_dir,output_vids_dir)
        quit()
    for file in os.listdir(vids_dir_path):
        vid = os.fsdecode(file)
        if vid.endswith(".y4m"):
            output_vid_string = "~/"+ output_vids_dir +"output_" + file.decode('UTF-8')[:-3]+"ivf"
            input_vid_string = "~/" + vids_dir +file.decode('UTF-8')
            os.system("(cd ~/"+ rav_dir +" && cargo run --release --bin rav1e -- "+input_vid_string + " -o " + output_vid_string+")")
            continue
        elif vid.endswith(".mp4"):
            input_vid_string = "~/" + vids_dir +file.decode('UTF-8')
            converted_input_vid = input_vid_string[:-3]+"y4m"
            os.system("ffmpeg -i "+ input_vid_string + " " + converted_input_vid)
            output_vid_string = "~/"+ output_vids_dir +"output_" + file.decode('UTF-8')[:-3]+"ivf"
            os.system("(cd ~/"+ rav_dir +" && cargo run --release --bin rav1e -- "+converted_input_vid + " -o " + output_vid_string+")")
        else:
            continue
    goto_stats = input("Videos have been encoded! Would you like to analyze these videos for more info (Y/N)?")
    while goto_stats not in ("Y","y","yes","Yes","N","n","no","No"):
        goto_stats = input("please enter Y or N")
    if goto_stats in ("Y","y","yes","Yes"):
        get_stats(vids_dir,output_vids_dir)
    elif goto_stats in ("N","n","no","No"):
        quit()

def get_stats(vids_dir,output_vids_dir):
    vids_dir_path, output_vids_dir_path = os.fsencode(vids_dir), os.fsencode(output_vids_dir)
    output_text = ""
    for source in os.listdir(vids_dir_path):
        for test in os.listdir(output_vids_dir_path):
            source_text = source.decode("UTF-8")
            test_text = test.decode("UTF-8")
            if source_text[:-3] == test_text[7:-3] and source_text[-3:] == "y4m":
                psnr_proc=subprocess.Popen("ffmpeg -i ~/"+output_vids_dir+test_text + " -i ~/"+vids_dir+source_text + " -lavfi \"[0:v] setpts=PTS-STARTPTS[out0]; [1:v] setpts=PTS-STARTPTS[out1]; [out0][out1] psnr=$logfile\" -f null - 2>&1 ;", shell= True,
         stdout = subprocess.PIPE)
                psnr_output=psnr_proc.communicate()[0].decode("UTF-8").split("\n")[-2]
                # os.system("ffmpeg -i " + source + " -i "+ test +" -lavfi \"[0:v] setpts=PTS-STARTPTS[out0]; [1:v] setpts=PTS-STARTPTS[out1]; [out0][out1] psnr=$logfile\" -f null - 2>&1 ;")
                vmaf_proc=subprocess.Popen("ffmpeg -i " + vids_dir+source_text + " -i " + output_vids_dir+test_text + " -f lavfi \ -lavfi '[0:v]setpts=N/(25*TB),scale=1920:1080[v0];[1:v]setpts=N/(25*TB),scale=1920:1080[v1];[v0][v1]libvmaf' -f null /dev/null", shell= True,
                stdout = subprocess.PIPE)
                vmaf_output=vmaf_proc.communicate()[0].decode("UTF-8")
                output_text+= "input: " + source_text + " output: " + test_text  + "\n" + psnr_output+ "\n"
    
    quit()
    return None

def quit():
    print("Goodbye!")
    return None

#ffmpeg -i ~/Downloads/in_vids/Animation_360P-3e52.y4m -i ~/Downloas/out_vids/Animation_360P-3e52.ivf -lavfi \"[0:v] setpts=PTS-STARTPTS[out0]; [1:v] setpts=PTS-STARTPTS[out1]; [out0][out1] psnr=$logfile\" -f null - 2>&1 ;
if __name__ == "__main__" :
        interaction_window()
