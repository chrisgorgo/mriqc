def create_report(subject_id, tsnr_file, realignment_parameters_file, mean_epi_file, mask_file, reg_file, fssubjects_dir, similarity_distribution, mean_FD_distribution, tsnr_distributions, output_file):
    import gc
    import pylab as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from mriqc.volumes import plot_mosaic, plot_distrbution_of_values
    from mriqc.correlation import plot_epi_T1_corregistration
    from mriqc.motion import plot_frame_displacement
    report = PdfPages(output_file)
    fig = plot_mosaic(mean_epi_file, title="Mean EPI", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    fig = plot_mosaic(mean_epi_file, "EPI mask", mask_file, figsize=(8.3, 11.7))
    report.savefig(fig, dpi=600)
    fig.clf()
    
    fig = plot_mosaic(tsnr_file, title="tSNR", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    fig = plot_distrbution_of_values(tsnr_file, mask_file, 
        "Subjects %s tSNR inside the mask" % subject_id, 
        tsnr_distributions, 
        "Distribution of median tSNR of all subjects", 
        figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    fig = plot_epi_T1_corregistration(mean_epi_file, reg_file, fssubjects_dir, subject_id, 
        similarity_distribution, figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
     
    fig = plot_frame_displacement(realignment_parameters_file, mean_FD_distribution, figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    report.close()
    gc.collect()
    plt.close()
    
    return output_file