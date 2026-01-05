"""Model the geometry of a torispherical head

e.g. Klöpperboden (DIN 28011), Korbbogenboden (DIN 28013)

"""
import numpy as np
from typing import Self
from pydantic import BaseModel, Field


class TorisphericalHead(BaseModel):
    """ Model for Torispherical Head geometry (DIN 28011, 28013).
    
    Default values corresponde to Klöpperboden r1=Da, r2=0.1Da, i.e., alpha1=1.0, alpha2=0.1.
    """
    external_diameter: float = Field(1000.0, gt=0)
    alpha1: float = Field(1.0, ge=0, le=2, description="r1 / Da factor")
    alpha2: float = Field(0.1, ge=0, le=2, description="r2 / Da factor")
    
    @property
    def crown_radius(self) -> float:
        return self.external_diameter * self.alpha1
    
    @property
    def knuckle_radius(self) -> float:
        return self.external_diameter * self.alpha2

    def set_crown_radius(self, r1: float) -> Self:
        self.alpha1 = r1 / self.external_diameter
        return self
    
    def set_knuckle_radius(self, r2: float) -> Self:
        self.alpha2 = r2 / self.external_diameter
        return self
    
    # --- Geometric Calculations ---
    @property
    def sin_theta(self) -> float:
        """
        Derived from geometrical equilibrium:
        Da/2 = r1*sin(theta) + r2(1 - sin(theta)
        """
        return (1 - 2 * self.alpha2) / (2 * (self.alpha1 - self.alpha2))
    
    @property
    def theta(self) -> float:
        """Transition angle in radians"""
        return np.arcsin(self.sin_theta)
    
    @property
    def knuckle_center_x(self) -> float:
        """Horizontal offset for the knuckle arc center"""
        return (self.external_diameter / 2) - self.knuckle_radius

    @property
    def knuckle_center_y(self) -> float:
        """Defined as 0 for the base weld line"""
        return 0.0
    
    @property
    def transition_point_x(self) -> float:
        """X-coordinate where Crown and Knuckle meet"""
        return self.crown_radius * self.sin_theta
    
    @property
    def transition_point_y(self) -> float:
        """Y-coordinate where Crown and Knuckle meet"""
        return self.knuckle_center_y + self.knuckle_radius * np.cos(self.theta)

    @property
    def crown_center_x(self) -> float:
        """Crown center is on the vessel axis (x=0)"""
        return 0.0

    @property
    def crown_center_y(self) -> float:
        """Vertical offset for the crown arc center"""
        # Calculated to match y at the transition point
        return self.transition_point_y - self.crown_radius * np.cos(self.theta)

    @property
    def volume(self) -> float:
        """Calculate the analytical internal volume of the head.

        Volume of straight flange (Zarge) is excluded.
        """
        r1 = self.crown_radius
        r2 = self.knuckle_radius
        xc = self.knuckle_center_x
        theta = self.theta
        sin_theta = self.sin_theta
        cos_theta = np.cos(theta)

        # 1. volume of spherical cap (crown/Kalotte)
        hc = r1 * (1 - cos_theta)
        volume_crown = (np.pi * hc**2 / 3) * (3 * r1 - hc)

        # 2. volume of the toroidal segment (knuckle/Krempe)
        term1 = xc**2 * cos_theta
        term2 = 2 * xc * r2 * (theta/2 - (np.sin(2*theta) / 4))
        term3 = r2**2 * (2/3 - cos_theta + (cos_theta**3 / 3))
        volume_knuckle = np.pi * r2 * (term1 + term2 + term3)
        return volume_crown + volume_knuckle

    def summary(self) -> str:
        """Returns a formatted string with key engineering dimensions."""
        h_total = self.crown_center_y + self.crown_radius
        
        lines = \
f"""--- Torispherical Head Summary ---,

Type: {'Klöpperboden' if self.alpha1==1.0 and self.alpha2==0.1 else 'Custom/Korbbogen'}
External Diameter (Da): {self.external_diameter:>8.2f}
Crown Radius (r1):      {self.crown_radius:>8.2f} (alpha1={self.alpha1})
Knuckle Radius (r2):    {self.knuckle_radius:>8.2f} (alpha2={self.alpha2})
Transition Angle (θ):   {np.degrees(self.theta):>8.2f}°
Transition Point (x,y): ({self.transition_point_x:.1f}, {self.transition_point_y:.1f})
Total Internal Height:  {h_total:>8.2f}
Internal Volume:        {self.volume}
----------------------------------
"""
        return lines


def kloepper_factory(external_diameter: float) -> TorisphericalHead:
    return TorisphericalHead(external_diameter=external_diameter)

def korbbogen_factory(external_diameter: float) -> TorisphericalHead:
    return TorisphericalHead(external_diameter=external_diameter, alpha1=0.8, alpha2=0.154)

