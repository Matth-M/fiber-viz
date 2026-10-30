# import numpy as np
# import scipy.signal as s
# from scipy.ndimage import gaussian_filter1d

# import FluoProcess


# def smooth_signal(signal, sigma):
#     return gaussian_filter1d(
#         np.asarray(signal),
#         sigma=sigma
#     )


# def find_peaks_algorithm(
#     signal,
#     prominence=2.3,
#     distance=1
# ):

#     peaks, properties = s.find_peaks(
#         np.asarray(signal),
#         prominence=prominence,
#         distance=distance
#     )

#     return peaks


# def argrelextrema_algorithm(
#     x,
#     signal,
#     percentile=88,
#     derivative_multiplier=1.55,
#     order=1
# ):

#     signal = np.asarray(signal)
#     x = np.asarray(x)

#     valleys = s.argrelmin(
#         signal,
#         order=order
#     )[0]

#     peaks = s.argrelmax(
#         signal,
#         order=order
#     )[0]

#     coordinates = []

#     for i in range(min(len(peaks), len(valleys))):

#         coordinates.append([
#             x[peaks[i]],
#             signal[peaks[i]]
#         ])

#         coordinates.append([
#             x[valleys[i]],
#             signal[valleys[i]]
#         ])

#     coordinates.sort(
#         key=lambda point: point[0]
#     )


#     derivatives = []
#     amplitudes = []

#     for i in range(len(coordinates) - 1):

#         delta_x = (
#             coordinates[i + 1][0]
#             - coordinates[i][0]
#         )

#         if delta_x == 0:
#             continue

#         derivative = (
#             coordinates[i + 1][1]
#             - coordinates[i][1]
#         ) / delta_x

#         amplitude = (
#             coordinates[i + 1][1]
#             - coordinates[i][1]
#         )

#         if derivative > 0:
#             derivatives.append(derivative)
#             amplitudes.append(amplitude)


#     if len(derivatives) == 0:
#         return np.array([], dtype=int)


#     mean_deriv = np.mean(derivatives)

#     deriv_threshold = np.percentile(
#         derivatives,
#         percentile
#     )

#     amp_threshold = np.percentile(
#         amplitudes,
#         percentile
#     )

#     peak_times = x[peaks]

#     interesting_x = []


#     for i in range(len(coordinates) - 1):

#         delta_x = (
#             coordinates[i + 1][0]
#             - coordinates[i][0]
#         )

#         if delta_x == 0:
#             continue

#         derivative = (
#             coordinates[i + 1][1]
#             - coordinates[i][1]
#         ) / delta_x

#         amplitude = (
#             coordinates[i + 1][1]
#             - coordinates[i][1]
#         )


#         positive_condition = (
#             derivative > 0
#             and
#             (
#                 (
#                     derivative
#                     > derivative_multiplier * mean_deriv
#                     and
#                     derivative > deriv_threshold
#                 )
#                 or
#                 (
#                     derivative
#                     > derivative_multiplier * mean_deriv
#                     and
#                     amplitude > amp_threshold
#                 )
#             )
#         )


#         if positive_condition:

#             candidate_x = coordinates[i + 1][0]

#             if candidate_x in peak_times:
#                 interesting_x.append(candidate_x)


#     indexes = []

#     for peak_x in interesting_x:

#         index = np.abs(
#             x - peak_x
#         ).argmin()

#         indexes.append(index)


#     return np.asarray(indexes, dtype=int)


# def fabrice_algorithm(df):

#     process = FluoProcess.FluoProcess.from_dataframe(
#         df.copy()
#     )

#     peaks = np.asarray(
#         process.filteredMaximas,
#         dtype=int
#     )

#     return peaks

