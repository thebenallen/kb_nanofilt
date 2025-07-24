# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import shutil

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.readsutilsClient import ReadsUtils
from .Utils.run_NanoFiltUtils import run_NanoFilt, upload_reads
from .Utils.createHtmlReport import HTMLReportCreator

from installed_clients.KBaseReportClient import KBaseReport

#END_HEADER


class kb_nanofilt:
    '''
    Module Name:
    kb_nanofilt

    Module Description:
    A KBase module: kb_nanofilt
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_nanofilt(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_nanofilt
        logging.info('Starting run_kb_nanofilt with params: {}'.format(params))
        logging.info('Downloading reads from ' + params['input_reads_ref'])

        # These three lines allow the app to download a reads-type file that would be in the narrative
        ru = ReadsUtils(self.callback_url)
        input_file_info = ru.download_reads({'read_libraries': [params['input_reads_ref']],
                                             'interleaved': 'false'})['files'][params['input_reads_ref']]
        logging.info('Downloaded reads from ' + str(input_file_info))

        output_reads_name = params['output_reads_name']
        output_reads_file = output_reads_name + ".fq"
        logging.info('Output reads name: ' + output_reads_file)

        # Run nanofilt
        logging.info('Running nanofilt')
        # "Results" are corrected files. "Reports" is, well, reports. Make a reportDirectory var. That gets passed into report_creator.create_html_report later on below.
        reportDirectory = os.path.join(self.shared_folder, 'Reports')
        reportFile = os.path.join(self.shared_folder, reportDirectory, 'index.html')
        resultsDirectory = os.path.join(self.shared_folder, 'Results')        

        # # Get the path from input_file_info['files']
        input_file_path = os.path.join(input_file_info['files']['fwd'])
        logging.info('Input file path: ' + input_file_path)

        returned_dict = run_NanoFilt(input_file_path, resultsDirectory, reportFile, params['length'], params['maxlength'], params['quality'], params['mingc'], params['maxgc'], params['headcrop'], params['tailcrop'])
        logging.info('Returned dictionary: ' + str(returned_dict))

        corrected_file_path = returned_dict['corrected_file_path']
        logging.info('Corrected file path: ' + corrected_file_path)
       
        # Copy the corrected file to the output file
        output_reads_filepath = os.path.join(resultsDirectory, output_reads_file)
        shutil.copy(corrected_file_path, output_reads_filepath)

        new_reads_upa = upload_reads(self.callback_url, output_reads_filepath, params['workspace_name'], output_reads_name, params['input_reads_ref'])        

        # Delete temp files (upload_reads should have already uploaded the corrected file)
        if os.path.exists(resultsDirectory):
            shutil.rmtree(resultsDirectory)

        objects_created = [{
                'ref': new_reads_upa,
                'description': 'Corrected reads library'
            }]

        # Create an HTML report
        report_creator = HTMLReportCreator(self.shared_folder, self.callback_url)
        report_html = report_creator.create_html_report(
            params['workspace_name'],
            output_reads_name,
            input_file_info['file_name'],
            input_file_info['file_size'],
            reportDirectory
        )

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_nanofilt

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_nanofilt return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
