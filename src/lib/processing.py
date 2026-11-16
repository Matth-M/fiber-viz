import numpy as np


def delta_f(ch410, ch470):
    fit_coeffs = np.polyfit(ch410, ch470, 1)
    isofit = np.polyval(fit_coeffs, ch410)
    return ((ch470 - isofit) / isofit) * 100
