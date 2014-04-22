from glob import glob
from mriqc.correlation import get_similarity_distribution
from mriqc.motion import get_mean_frame_displacement_disttribution
from mriqc.volumes import get_median_distribution
from mriqc.reports import create_report
import pandas as pd
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import Function


if __name__ == '__main__':
    subject_id = "0179454"#"0199155"#
    #subject_id = "0179005"
    data_dir = "/scr/kalifornien1/data/nki_enhanced/preprocessed_fmri/"
    
    trs = [645, 1400, 2500]
    wf = Workflow("reports")
    wf.base_dir = "/scr/adenauer1/PowerFolder/Dropbox/nki_reports/workdir"
    
    for tr in trs:
        print tr
        subjects = [i.split("/")[-1] for i in glob(data_dir + "results%s/*"%str(tr))]
        subjects.sort()
         
        #generating distributions
        mincost_files = [data_dir + "results%s/%s/preproc/bbreg/afni_%s_register.dat.mincost"%(tr, subject, subject) for subject in subjects]
        similarity_distribution = get_similarity_distribution(mincost_files)
        similarity_distribution = dict(zip(subjects, similarity_distribution))
         
        realignment_parameters_files = [data_dir + "results%s/%s/preproc/motion/afni_realignment_parameters.par"%(tr, subject) for subject in subjects]
        mean_FD_distribution = get_mean_frame_displacement_disttribution(realignment_parameters_files)
         
        tsnr_files = [data_dir + "results%s/%s/preproc/tsnr/%s_r00_afni_tsnr.nii.gz"%(tr, subject, subject) for subject in subjects]
        mask_files = [data_dir + "results%s/%s/preproc/mask/%s_brainmask.nii"%(tr, subject, subject) for subject in subjects]
        tsnr_distributions = get_median_distribution(tsnr_files, mask_files)
        
        df = pd.DataFrame(zip(subjects, similarity_distribution.values(), mean_FD_distribution, tsnr_distributions), columns = ["subject_id", "coregistration quality", "Mean FD", "Median tSNR"])
        df.to_csv("/scr/adenauer1/PowerFolder/Dropbox/nki_reports/%s/summary.csv"%tr)
        
        for subject_id in subjects:
            print subject_id
            #setting paths for this subject
            tsnr_file = data_dir + "results%s/%s/preproc/tsnr/%s_r00_afni_tsnr.nii.gz"%(tr, subject_id, subject_id)
            timeseries_file = data_dir + "results%s/%s/preproc/output/bandpassed/fwhm_0.0/%s_r00_afni_bandpassed.nii.gz"%(tr, subject_id, subject_id)
            realignment_parameters_file = data_dir + "results%s/%s/preproc/motion/afni_realignment_parameters.par"%(tr, subject_id)
    
            mean_epi_file = glob(data_dir + "results%s/%s/preproc/mean/*%s*.nii.gz"%(tr, subject_id, tr))[0]
            mask_file = data_dir + "results%s/%s/preproc/mask/%s_brainmask.nii"%(tr, subject_id, subject_id)
            reg_file = data_dir + "results%s/%s/preproc/bbreg/afni_%s_register.dat"%(tr, subject_id, subject_id)
            fssubjects_dir = "/scr/kalifornien1/data/nki_enhanced/freesurfer/"
    
            mincost_file = data_dir + "results%s/%s/preproc/bbreg/afni_%s_register.dat.mincost"%(tr, subject_id, subject_id)
            
            output_file = "/scr/adenauer1/PowerFolder/Dropbox/nki_reports/%s/%s_report.pdf"%(tr, subject_id)
            
#             report = Node(Function(input_names=['subject_id', 
#                                                 'tsnr_file', 
#                                                 'realignment_parameters_file', 
#                                                 'mean_epi_file', 
#                                                 'mask_file', 
#                                                 'reg_file', 
#                                                 'fssubjects_dir', 
#                                                 'similarity_distribution', 
#                                                 'mean_FD_distribution', 
#                                                 'tsnr_distributions', 
#                                                 'output_file'], 
#                                    output_names=['out'],
#                                    function = create_report), name="report_%s_%s"%(tr,subject_id))
#             report.inputs.subject_id = subject_id
#             report.inputs.tsnr_file = tsnr_file
#             report.inputs.realignment_parameters_file = realignment_parameters_file
#             report.inputs.mean_epi_file = mean_epi_file
#             report.inputs.mask_file = mask_file
#             report.inputs.reg_file = reg_file
#             report.inputs.fssubjects_dir = fssubjects_dir
#             report.inputs.similarity_distribution = similarity_distribution
#             report.inputs.mean_FD_distribution = mean_FD_distribution
#             report.inputs.tsnr_distributions = tsnr_distributions
#             report.inputs.output_file = output_file
#             wf.add_nodes([report])
#             
#     wf.run(plugin="CondorDAGMan")
        