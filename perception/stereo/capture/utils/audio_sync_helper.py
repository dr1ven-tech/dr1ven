
import sys
from aubio import source
import numpy as np 
import argparse

frame_interval = 1/30.0

def get_max_time(filename, samplerate = 0, block_size = 4096, ax = None, downsample = 2**4, stop_at = None):
    import matplotlib.pyplot as plt
    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    hop_s = block_size

    allsamples =np.zeros(0,)
    downsample = downsample  # to plot n samples / hop_s

    should_stop_early = True

    a = source(filename, samplerate, hop_s)            # source file
    if samplerate == 0: samplerate = a.samplerate
    if stop_at == None: should_stop_early = False

    total_frames = 0
    while True:
        samples, read = a()
        # keep some data to plot it later
        new_samples = abs(samples)
        allsamples = np.hstack([allsamples, new_samples])
        total_frames += read
        if total_frames > stop_at*samplerate and should_stop_early: break
        if read < hop_s: break

    offset_samples = np.hstack([allsamples[1:],[0]])
    derivative_samples = offset_samples - allsamples
    t_max_idx = np.argmax(allsamples, axis=0)
    derivative_max_idx = np.argmax(derivative_samples, axis=0)

    # normalize
    derivative_samples = derivative_samples /  derivative_samples[derivative_max_idx]

    allsamples_times = [ ( float (t) ) for t in range(len(allsamples)) ]
    t_max = allsamples_times[t_max_idx]
    derivative_t_max = allsamples_times[derivative_max_idx]
    print("max is reached at %02d:%02d:%03d" % (t_max/float(samplerate)/60, (t_max/float(samplerate))%60, (t_max*1000.0/float(samplerate))%1000 ))

    ax.plot(allsamples_times,  allsamples, '-b', derivative_samples, '-g')
    ax.axis(xmin = allsamples_times[0], xmax = allsamples_times[-1])
    set_xlabels_sample2time(ax, allsamples_times[-1], samplerate)

    return ax, t_max/float(samplerate), derivative_t_max/float(samplerate)

def set_xlabels_sample2time(ax, latest_sample, samplerate):
    ax.axis(xmin = 0, xmax = latest_sample)	
    if latest_sample / float(samplerate) > 60:
        ax.set_xlabel('time (mm:ss)')
        ax.set_xticklabels([ "%02d:%02d" % (t/float(samplerate)/60, (t/float(samplerate))%60) for t in ax.get_xticks()[:-1]], rotation = 50)
    else:
        ax.set_xlabel('time (ss.mm)')
        ax.set_xticklabels([ "%02d.%02d" % (t/float(samplerate), 100*((t/float(samplerate))%1) ) for t in ax.get_xticks()[:-1]], rotation = 50)

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--master_audio', type=str, help="reference audio for time")
    parser.add_argument('--slave_audio', type=str, help="second audio")
    # parser.add_argument('--start_time', type=str, help="start_time express like ss in ffmpeg")
    parser.add_argument('--stop_at', type=float, help="stop finding audio max at")
    # parser.add_argument('--number_of_frames', type=int, help="number of frames to extract")
    args = parser.parse_args()

    assert args.master_audio is not None
    assert args.slave_audio is not None

    ax, master_max_time, master_derivative_max_time = get_max_time(args.master_audio, stop_at = args.stop_at)
    plt.show()

    ax, slave_max_time, slave_derivative_max_time = get_max_time(args.slave_audio, stop_at = args.stop_at)
    plt.show()

    delta_t_max = slave_max_time - master_max_time
    print('slave should start %02d:%02d:%03d later' % (delta_t_max/60, delta_t_max%60, delta_t_max*1000%1000 ))
    delta_derivative_t_max = slave_derivative_max_time - master_derivative_max_time
    print('slave should start %02d:%02d:%03d later according to derivative' % (delta_derivative_t_max/60, delta_derivative_t_max%60, delta_derivative_t_max*1000%1000 ))

    closest_frame = round(delta_derivative_t_max * 30.0)/30
    #take a time just after (0.1 of frame interval) the frame to be sure to pick the right frame
    time_for_slave_sync = delta_derivative_t_max + 0.1 * frame_interval
    final_offset = delta_t_max - closest_frame
    print('slave should start at %02d:%02d:%03d' % (time_for_slave_sync/60, time_for_slave_sync%60, time_for_slave_sync*1000%1000 ))
    print('then slave will be %02d:%02d:%03d late' % (final_offset/60, final_offset%60, final_offset*1000%1000 ))
        
