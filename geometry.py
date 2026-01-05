import numpy as np
import numpy.typing as npt

type Float1DVector = npt.NDArray[np.float64]


def get_kloepper_profile(
    external_diameter: float, num_points: int = 100
) -> tuple[Float1DVector, Float1DVector]:
    """Calculate 2D profile coordinates for a Klöpper head (DIN 28011).

    Args:
        external_diameter: external diameter of cilindrical vessel in a given unit system. 
            Returned values are to be interpreted as having the same unit as the inputed diameter.
        num_points: numper of points for the generated 2D profile.

    Returns:
        (x_vals, y_vals) representing the cross-section from center to edge.

    """
    Da = external_diameter
    r1 = Da  # crown radius (Kalotte)
    r2 = 0.1 * Da  # knucke radius (Krempe)

    # Da/2 = r1*sin(theta) + r2(1 - sin(theta)
    # this leads to the derivation sin(theta) = 4/9
    sin_theta = 4 / 9
    theta = np.arcsin(sin_theta)

    # boundary x-coordinate, where crown meets knuckle
    x_trans = r1 * sin_theta

    # knuckle center ends at x = Da/2, y = 0
    y_center_knuckle = 0
    x_center_knuckle = (Da / 2) - r2

    # find center of the crown (here x_center_crown = 0 by definition)
    y_trans = y_center_knuckle + r2 * np.cos(theta)
    y_center_crown = y_trans - r1 * np.cos(theta)

    # generate points
    x_vals = np.linspace(0, Da / 2, num_points)
    y_vals = np.where(
        x_vals <= x_trans,
        y_center_crown + np.sqrt(r1**2 - x_vals**2),
        y_center_knuckle + np.sqrt(r2**2 - (x_vals - x_center_knuckle) ** 2),
    )

    return x_vals, np.array(y_vals)


def get_torispherical_profile(
    external_diameter: float,
    alpha1: float = 1.0,
    alpha2: float = 0.1,
    num_points: int = 100
) -> tuple[Float1DVector, Float1DVector]:
    """Calculate 2D profile coordinates for an arbitrary torispherical head.

    Defaults to Klöpperboden (alpha1=1.0, alpha2=0.1).
    For Korbbogenboden, use alpha1=0.8, alpha2=0.154.

    Args:
        external_diameter: external diameter of cilindrical vessel in a given unit system. 
            Returned values are to be interpreted as having the same unit as the inputed diameter.
        alpha1: factor of proportionality between crown radius (r₁) and external diameter (Dₐ), i.e., r₁:= α₁·Dₐ.
        alpha2: factor of proportionality between knuckle radius (r₂) and external diameter (Dₐ), i.e., r₂:= α₂·Dₐ.
        num_points: numper of points for the generated 2D profile.

    Returns:
        (x_vals, y_vals) representing the cross-section from center to edge.

    """
    Da = external_diameter
    r1 = alpha1 * Da  # crown radius (Kalotte)
    r2 = alpha2 * Da  # knuckle radius (Krempe)
    
    # Da/2 = r1*sin(theta) + r2(1 - sin(theta)
    # this leads to the derivation sin(theta)
    sin_theta = (1 - 2 * alpha2) / (2 * (alpha1 - alpha2))
    theta = np.arcsin(sin_theta)

    # boundary x-coordinate, where crown meets knuckle
    x_trans = r1 * sin_theta

    # knuckle center ends at x = Da/2, y = 0
    y_center_knuckle = 0
    x_center_knuckle = (Da / 2) - r2

    # find center of the crown (here x_center_crown = 0 by definition)
    y_trans = y_center_knuckle + r2 * np.cos(theta)
    y_center_crown = y_trans - r1 * np.cos(theta)

    # generate points
    x_vals = np.linspace(0, Da / 2, num_points)
    y_vals = np.where(
        x_vals <= x_trans,
        y_center_crown + np.sqrt(r1**2 - x_vals**2),
        y_center_knuckle + np.sqrt(r2**2 - (x_vals - x_center_knuckle) ** 2),
    )

    return x_vals, np.array(y_vals)

