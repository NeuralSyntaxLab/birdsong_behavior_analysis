#%% Imports:
import sys
sys.path.append('..')
from helper_functions_manage_annotation_files.functions_to_convert_between_tweet_and_csv_annotation_files import *
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.io import wavfile
import birdsonganalysis as bsa

# %%
def calculate_partial_SAT_features_from_signal(sig, samplerate, freq_range=256, fft_size=512, fft_step=40):
    """
    Use the implementation of SAT (birdsonganalysis by Paul Ecoffet) on an audio signal.
    Note: We use our fork (https://github.com/NeuralSyntaxLab/birdsonganalysis) because 
    we adapted functions to return signal time points for future alignments.

    Parameters
    ----------
    sig : list or ndarray of float.
        The signal to be processed.
    samplerate : float or int
        The sampling rate of the signal.
    
    Optional Parameters
    ----------
    freq_range : int (default: 256)
        The maximal frequency bin used in calculations (currently the minimal is 25).
    fft_size : int (default: 512)
        Number of time points used for FFTs.
    fft_step : int  (default: 40).
        Number of time points between windows used for calculating FFTs.

    Returns
    -------
    output_df : Dataframe
        Each row is a time point.
        Columns are: 'time','pitch','amplitude','entropy','am','fm','goodness'
    """
    all_f = bsa.all_song_features(sig, samplerate, freq_range=freq_range, fft_size=fft_size, fft_step=fft_step)
    output_df = pd.DataFrame({k:all_f[k] for k in ['time','pitch','amplitude','entropy','am','fm','goodness']})
    return output_df

def add_partial_SAT_features_to_annotation_df(annot_df,path_to_audio_files, freq_range=256, fft_size=512, fft_step=40):
    """
    Use the implementation of SAT (birdsonganalysis by Paul Ecoffet) to add mean and median feature values
    to all syllables in a vak-format DataFrame annotation.
    Note: We use our fork (https://github.com/NeuralSyntaxLab/birdsonganalysis) because 
    we adapted functions to return signal time points for future alignments.

    Parameters
    ----------
    annot_df : DataFrame
        The annotation DataFrame to edit.
    path_to_audio_files : string or Path
        Path to the audio files referenced in the annotation file.
    
    Optional Parameters
    ----------
    freq_range : int (default: 256)
        The maximal frequency bin used in calculations (currently the minimal is 25).
    fft_size : int (default: 512)
        Number of time points used for FFTs.
    fft_step : int  (default: 40).
        Number of time points between windows used for calculating FFTs.

    Returns
    -------
    output_df : Dataframe
        The input where we add in each row the mean and median values of the features:
        'pitch','amplitude','entropy','am','fm','goodness'

    Example Usage
    -------------
    path_to_audio = '/Users/yardenc/Dropbox (Weizmann Institute)/temp_share_canary_data/llb3_songs'
    annot_df = pd.read_csv('/Users/yardenc/Dropbox (Weizmann Institute)/temp_share_canary_data/llb3_annot.csv')
    path_to_temp_results = '/Users/yardenc/Desktop/llb3_annot_with_acoustics.csv'
    df = add_partial_SAT_features_to_annotation_df(annot_df,path_to_audio)
    f.to_csv(path_to_temp_results)
    """
    syllable_features = ['pitch','amplitude','entropy','am','fm','goodness']
    median_syllable_features_dict = {k:[] for k in syllable_features}
    mean_syllable_features_dict = {k:[] for k in syllable_features}
    path_to_audio_files = Path(path_to_audio_files)
    keys = annot_df['audio_file'].unique()
    len_keys = len(keys)
    curr_idx = 1
    for key in keys:
        print("processing file {} out of {}".format(curr_idx,len_keys))
        curr_idx += 1
        file_path = Path(path_to_audio_files,key)
        sr, sig = wavfile.read(file_path)
        curr_df = annot_df[annot_df['audio_file'] == key]
        segFileStartTimes = list(curr_df['onset_s'].astype(float))
        segFileEndTimes = list(curr_df['offset_s'].astype(float))
        acoustic_df = calculate_partial_SAT_features_from_signal(sig,sr,freq_range=freq_range,fft_size=fft_size,fft_step=fft_step)
        for t_start,t_end in zip(segFileStartTimes,segFileEndTimes):
            temp_acoustic_df = acoustic_df[acoustic_df['time'].between(t_start,t_end)]
            median_features = temp_acoustic_df.median()
            mean_features = temp_acoustic_df.mean()
            for k in syllable_features:
                median_syllable_features_dict[k] = median_syllable_features_dict[k] + [median_features[k]]
                mean_syllable_features_dict[k] = mean_syllable_features_dict[k] + [mean_features[k]]
    for k in syllable_features:
        annot_df['mean_' + k] = mean_syllable_features_dict[k]
        annot_df['median_' + k] = median_syllable_features_dict[k]
    return annot_df
# %%

# %%