import math
import numpy as np
import csv
from autoseas.lookUpTable import loadTable, valueFromTable

def calculate_fully_developed_wave_height(V_stc, g):
    """
    Calculate the fully developed wave height using Breugem and Holthuijsen (2006) formulation.
    Reference: Breugem, W., and L. Holthuijsen, 2006. "Generalized shallow water wave growth from Lake George."
               Journal of Waterway, Port, Coastal, and Ocean Engineering, 133, 173.

    Parameters:
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.
    - g (float): Acceleration due to gravity in m/s^2.

    Returns:
    - float: Fully developed wave height.
    """
    H_max = 0.2433 * abs(V_stc)**2 / g
    return H_max

def calculate_depth_term(g, D, V_stc):
    """
    Calculate the depth term in the wave height formula.

    Parameters:
    - g (float): Acceleration due to gravity in m/s^2.
    - D (float): Water depth in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Depth term.
    """
    depth_term = math.tanh(0.343 * (g * D / abs(V_stc)**2)**1.14)
    return depth_term

def calculate_fetch_term(g, F, V_stc):
    """
    Calculate the fetch term in the wave height formula.

    Parameters:
    - g (float): Acceleration due to gravity in m/s^2.
    - F (float): Fetch distance in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Fetch term.
    """
    fetch_term = math.tanh(0.000414 * (g * F / abs(V_stc)**2)**0.79)
    return fetch_term

def calculate_wave_height(H_max, depth_term, fetch_term):
    """
    Calculate the fully developed wave height using the depth and fetch terms.

    Parameters:
    - H_max (float): Fully developed wave height.
    - depth_term (float): Depth term.
    - fetch_term (float): Fetch term.

    Returns:
    - float: Wave height.
    """
    H = H_max * (depth_term * math.tanh(fetch_term * depth_term))
    return H

def calculate_fully_developed_wave_period(V_stc, g):
    """
    Calculate the fully developed wave period using additional equations.
    Reference: Holthuijsen, L. H., 2007. "Waves in Oceanic and Coastal Waters." Cambridge University Press, 404 pp.

    Parameters:
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.
    - g (float): Acceleration due to gravity in m/s^2.

    Returns:
    - float: Fully developed wave period.
    """
    T_max = 7.69 * abs(V_stc) / g
    return T_max

def calculate_depth_term_period(g, D, V_stc):
    """
    Calculate the depth term in the wave period formula.

    Parameters:
    - g (float): Acceleration due to gravity in m/s^2.
    - D (float): Water depth in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Depth term for wave period.
    """
    depth_term_period = math.tanh(0.1 * (g * D / abs(V_stc)**2)**2.01)
    return depth_term_period

def calculate_fetch_term_period(g, F, V_stc):
    """
    Calculate the fetch term in the wave period formula.

    Parameters:
    - g (float): Acceleration due to gravity in m/s^2.
    - F (float): Fetch distance in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Fetch term for wave period.
    """
    fetch_term_period = math.tanh(0.000000277 * (g * F / abs(V_stc)**2)**1.45)
    return fetch_term_period

def calculate_wave_period(T_max, depth_term_period, fetch_term_period):
    """
    Calculate the fully developed wave period using the depth and fetch terms.

    Parameters:
    - T_max (float): Fully developed wave period.
    - depth_term_period (float): Depth term for wave period.
    - fetch_term_period (float): Fetch term for wave period.

    Returns:
    - float: Wave period.
    """
    T = T_max * (depth_term_period * math.tanh(fetch_term_period * depth_term_period))**0.18
    return T

# Example usage:
V_stc = 10.0  # sustained wind speed at 10-meter height in m/s
g = 9.81     # acceleration due to gravity in m/s^2
D = 5.0      # water depth in meters
F = 10000.0  # fetch distance in meters

H_max = calculate_fully_developed_wave_height(V_stc, g)
depth_term = calculate_depth_term(g, D, V_stc)
fetch_term = calculate_fetch_term(g, F, V_stc)
wave_height = calculate_wave_height(H_max, depth_term, fetch_term)

T_max = calculate_fully_developed_wave_period(V_stc, g)
depth_term_period = calculate_depth_term_period(g, D, V_stc)
fetch_term_period = calculate_fetch_term_period(g, F, V_stc)
wave_period = calculate_wave_period(T_max, depth_term_period, fetch_term_period)

print(f"The fully developed wave height is: {wave_height} meters")
print(f"The fully developed wave period is: {wave_period} seconds")