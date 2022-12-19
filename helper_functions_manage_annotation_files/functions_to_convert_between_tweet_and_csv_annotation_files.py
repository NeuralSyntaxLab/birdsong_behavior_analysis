#%% Imports
import scipy.io as cpio
import pandas as pd
import numpy as np
from pathlib import Path
import mat73
import matplotlib.pyplot as plt
# %%
def tweet_to_df(path_to_tweet,path_to_audio_files,path_to_csv=None,additional_fields=None):
    # 
    """Load a (Matlab) tweet annotation file and 
    return a dataframe as in crowsetta or vak.

    Parameters
    ----------
    path_to_tweet : Path
        Points to the Matlab annotation file to be converted.
    path_to_audio_files : Path
        Points to the folder containing the audio files 
        referenced by the annotation file.
    
    Optional Parameters
    ----------
    path_to_csv : Path (default: None)
        Points to the csv annotation file to be saved.
    additional_fields : list of strings
        Names of non-mandatory fields that exist 
        in the annotation file and should be used.
        These must be syllable-level fields, like acoustic features, 
        and not file level, like the file number.

    Returns
    -------
    output_df : Dataframe
        The annotations of vocalizations as a pandas dataframe.
    """
    path_to_tweet = Path(path_to_tweet)
    path_to_audio_files = Path(path_to_audio_files)
    try:
        fl = cpio.loadmat(path_to_tweet,simplify_cells=True)
        keys = fl['keys'].astype(str)
        elements = fl['elements']
    except:
        print('Matlab file version is 7.3 or higher')
        fl = mat73.loadmat(path_to_tweet)
        keys = np.array(fl73['keys'])
        elements = fl73['elements']
    # Now created df
    label = []; onset_s = []; offset_s = []; onset_Hz = []; offset_Hz = []; audio_file = []; annot_file = []; sequence = []; annotation = []
    if additional_fields != None:
        more_fields = {fld: [] for fld in additional_fields}
    else:
        more_fields = {}
    num_file = 0
    samp_wav_path = Path(path_to_audio_files,Path(keys[0]).stem + Path(keys[0]).suffix)
    samplerate, data = cpio.wavfile.read(str(samp_wav_path))
    for element,key in zip(elements,keys):
        curr_label = list(element['segType'].astype(int))
        curr_onset_s = list(element['segFileStartTimes'].astype(float))
        curr_offset_s = list(element['segFileEndTimes'].astype(float))
        curr_onset_Hz = list(np.round(samplerate * element['segFileStartTimes'].astype(float)).astype(int))
        curr_offset_Hz = list(np.round(samplerate * element['segFileEndTimes'].astype(float)).astype(int))
        curr_audio_file = [str(key)]*len(curr_label)
        curr_annot_file = [str(path_to_tweet)]*len(curr_label)
        curr_sequence = [0]*len(curr_label)
        curr_annotation = [num_file]*len(curr_label)
        num_file = num_file + 1
        label = label + curr_label; onset_s = onset_s + curr_onset_s; offset_s = offset_s + curr_offset_s; onset_Hz = onset_Hz + curr_onset_Hz; offset_Hz = offset_Hz + curr_offset_Hz; audio_file = audio_file + curr_audio_file; annot_file = annot_file + curr_annot_file; sequence = sequence + curr_sequence; annotation = annotation + curr_annotation;
        if additional_fields != None:
            for tmp_key in more_fields.keys:
                more_fields[tmp_key] = more_fields[tmp_key] + list(element[tmp_key])
    output_dict = {'label':label,
                   'onset_s':onset_s,
                   'offset_s':offset_s,
                   'onset_Hz':onset_Hz,
                   'offset_Hz':offset_Hz,
                   'audio_file':audio_file,
                   'annot_file':annot_file,
                   'sequence':sequence,
                   'annotation':annotation} | more_fields
    output_df = pd.DataFrame(output_dict)
    if path_to_csv != None:
        path_to_csv = Path(path_to_csv)
        output_df.to_csv(path_to_csv)
    return output_df


def df_to_tweet(input_df,path_to_tweet=None,additional_fields=None):
    # 
    """Take a pandas Dataframe and convert it to the tweet (keys, elements) format. 
    Save the annotation matlab file if needed.

    Parameters
    ----------
    input_df : pandas Dataframe
        The annotations of vocalizations as a pandas dataframe.
    
    Optional Parameters
    ----------
    path_to_tweet : Path (default: None)
        Points to the tweet (Matlab) annotation file to be saved.
    additional_fields : list of strings
        Names of non-mandatory fields that exist 
        in the annotation file and should be used.
        These must be syllable-level fields, like acoustic features, 
        and not file level, like the file number.

    Returns
    -------
    keys : array of strings
        All audio file names.
    elements : list of dicts
        All per-file annotation dicts
    """
    keys = input_df['audio_file'].unique()
    elements = []
    for key in keys:
        curr_file = str(key)
        curr_filenum = curr_file.split('_')[1]
        curr_df = input_df[input_df['audio_file'] == key]
        segType = np.array(curr_df['label'].astype(float))
        segFileStartTimes = list(curr_df['onset_s'].astype(float))
        segFileEndTimes = list(curr_df['offset_s'].astype(float))
        if additional_fields != None:
            more_fields = {fld: list(curr_df[fld]) for fld in additional_fields}
        else:
            more_fields = {}
        element = {'filenum':curr_filenum,
                   'segType':segType,
                   'segFileStartTimes':segFileStartTimes,
                   'segFileEndTimes':segFileEndTimes} | more_fields
        elements.append(element)
    if path_to_tweet != None:
        path_to_tweet = Path(path_to_tweet)
        cpio.savemat(path_to_tweet,{'keys':keys,'elements':elements})
    return keys,elements
