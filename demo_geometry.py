import matplotlib.pyplot as plt
import numpy as np
from geometry import get_kloepper_profile

def main() -> None:
    # 1. Generate the profile for a 1000mm diameter head
    Da = 1000
    x, y = get_kloepper_profile(Da, num_points=500)

    # 2. Mirror for full view
    x_full = np.concatenate((-x[::-1], x))
    y_full = np.concatenate((y[::-1], y))

    # 3. Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(x_full, y_full, label='DIN 28011 Profile', linewidth=2)

    # Add engineering markers
    plt.axhline(0, color='black', lw=1) # Weld line / Base
    plt.axvline(0, color='black', lw=0.5, linestyle='--') # Centerline

    # Highlight the transition points (theta)
    sin_theta = 4/9
    x_trans = Da * sin_theta
    y_trans = y[np.abs(x - x_trans).argmin()]

    plt.plot([-x_trans, x_trans], [y_trans, y_trans], 'ro', markersize=4, label='Transition Point')

    # Formatting
    plt.title(f"Klöpperboden Profile (Da = {Da}mm)", fontsize=14)
    plt.xlabel("Radius [mm]")
    plt.ylabel("Height [mm]")
    plt.axis('equal') # CRITICAL for engineering: ensures geometry isn't distorted
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    plt.legend()

    plt.show()

if __name__ == "__main__":
    main()

