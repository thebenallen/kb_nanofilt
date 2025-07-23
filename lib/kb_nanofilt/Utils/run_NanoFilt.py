import subprocess
import os
from installed_clients.readsutilsClient import ReadsUtils
from installed_clients.DataFileUtilClient import DataFileUtil

def run_NanoFilt(input_file, result_dir, report_file, length, maxlength, quality, mingc, maxgc, headcrop, tailcrop, threads=10):
    try:
        # Construct the NanoFilt command with additional parameters
        command = [
            'NanoFilt',
            '-l', str(length),
            '--maxlength', str(maxlength),
            '-q', str(quality),
            '--mingc', str(mingc),
            '--maxgc', str(maxgc),
            '--headcrop', str(headcrop),
            '--tailcrop', str(tailcrop),
            '-t', str(threads)
        ]
        
        # Run the NanoFilt command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Create a directory for report_file if it doesn't exist
        if not os.path.exists(os.path.dirname(report_file)):
            os.makedirs(os.path.dirname(report_file))

        # Create a directory for result_dir if it doesn't exist
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        # Write the output to the specified HTML-formatted file
        with open(report_file, 'w') as f:
            f.write("<html><body><pre>")
            f.write(result.stderr)
            f.write("</pre></body></html>")
            
        print(f"NanoFilt command executed successfully. Output saved to {report_file}\n")

        # Get the file name's prefix to the left of the . from input_file. Ignore the path.
        prefix = input_file.split('/')[-1].split('.')[0]
        # extension = input_file.split('/')[-1].split('.')[1]

        # Return in a dictionary two file names found in the result_dir folder: The first has a .html prefix and the second has '.cor.' in the name and its filename prefix is the same as the input file's prefix.
        return {
            # 'console_report_file': report_file, # No need to return - input parameter is not altered.
            'corrected_file_path': result_dir + '/' + [f for f in os.listdir(result_dir) if prefix in f][0] #,
            # 'corrected_file_name': [f for f in os.listdir(result_dir) if prefix in f][0]
        }

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running NanoFilt: {e}")


def upload_reads(callback_url, reads_file, ws_name, reads_obj_name, source_reads_upa, isInterleaved):
    """
    callback_url = as usual.
    reads_file = full path to the reads file to upload
    ws_name = the workspace to use for uploading the reads file
    reads_obj_name = the name of the new reads object to save as
    source_reads = if not None, the source UPA for the original reads file.
    """
    # unfortunately, the ReadsUtils only accepts uncompressed fq files- this should
    # be fixed on the KBase side
    dfu = DataFileUtil(callback_url)
    reads_unpacked = dfu.unpack_file({'file_path': reads_file})['file_path']

    ru = ReadsUtils(callback_url)
    new_reads_upa = ru.upload_reads({
        'fwd_file': reads_unpacked,
        'interleaved': isInterleaved,
        'wsname': ws_name,
        'name': reads_obj_name,
        'source_reads_ref': source_reads_upa
    })['obj_ref']
    print('saved ' + str(reads_unpacked) + ' to ' + str(new_reads_upa))
    return new_reads_upa
