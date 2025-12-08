from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
import numpy as np


def main():
    print("--- Running Functional Pressure Vessel Design Example ---")

    # 1. Define Inputs
    design_inputs = {
        "internal_diameter_mm": 1200,
        "cylindrical_shell_length_mm": 3000,
        "design_pressure_bar": 3.0,
        "design_temperature_c": 100.0,
        "material_grade": MaterialGrade._1_4404,
    }

    try:
        # 2. Validate Inputs and Create Parameter Object
        params = VesselParameters(**design_inputs)

        # 3. Perform Functional Calculation
        results = perform_vessel_design(params)

        # 4. Display Results
        print("\nDesign Inputs (Pydantic Validated):")
        print(f"  Internal Diameter D_i: {params.D_i} mm")
        print(f"  Design Stress f: {params.f} MPa")
        print(f"  Design Pressure P: {params.P_design_MPa} MPa")

        print("\n--- Final Design Results (EN 13445) ---")
        print(f"Required Shell Thickness: {results['e_shell_required_mm']} mm")
        print(f"Required Head Thickness: {results['e_head_required_mm']} mm")
        print(f"**Recommended Nominal Thickness:** {results['e_nominal_mm']} mm")

    except Exception as e:
        print(f"An error occurred during design: {e}")


class MaterialGrade(StrEnum):
    _1_4404 = "1.4404"


# Simplified Allowable Stress (f) lookup
def get_design_stress(material_grade: MaterialGrade, T_design_C: float) -> float:
    """Returns the Nominal Design Stress (f) in MPa based on EN 13445-3 (simplified)."""
    if material_grade == MaterialGrade._1_4404 and T_design_C <= 100.0:
        return 120.0  # MPa (N/mm²)
    # Add logic for other temperatures/materials here
    raise ValueError(
        f"Material {material_grade} at {T_design_C}°C not supported or requires detailed lookup."
    )


class VesselParameters(BaseModel):
    """
    Calculates required wall thicknesses for a cylindrical pressure vessel
    with torispherical (Klöpper) heads based on EN 13445-3 principles.
    """

    # Design Inputs
    internal_diameter_mm: PositiveInt = Field(
        ..., description="Internal Diameter (D_i) in mm"
    )
    cylindrical_shell_length_mm: PositiveInt = Field(
        ..., description="Cylindrical Shell Length (L) in mm"
    )
    design_pressure_bar: PositiveFloat = Field(
        3.0, description="Design Pressure (P_design) in bar"
    )
    design_temperature_c: float = Field(
        100.0, description="Design Temperature (T_design) in °C"
    )
    material_grade: MaterialGrade = Field(
        MaterialGrade._1_4404, description="Material Grade"
    )

    # Derived Constants

    # Design Factors (Based on NDT/Welding Quality)
    # z = Weld Joint Coefficient (1.0 for Class 1 welds/full NDT)
    z: float = Field(1.0, description="Weld Joint Coefficient")
    # Allowances (corrosion c0 + manufacturing c1)
    # Total allowance (e.g., 0.5 mm corrosion + 0.5 mm tolerance)
    c: float = Field(1.0, description="Total Allowance (mm)")

    @property
    def f(self) -> float:
        """Nominal Design Stress (MPa)"""
        return get_design_stress(self.material_grade, self.T_design_C)

    @property
    def R_i_mm(self) -> PositiveInt:
        """Crown Radius (mm) Klöpperboden (DIN 28011)"""
        return self.D_i_mm  # R_i = D_i for Klöpper head

    R_i = R_i_mm

    @property
    def r_i_mm(self) -> PositiveFloat:
        """Knuckle Radius (mm) Klöpperboden (DIN 28011)"""
        return 0.1 * self.D_i_mm  # r_i = 0.1 * D_i for Klöpper head

    r_i = r_i_mm

    @property
    def D_i(self):
        return self.internal_diameter_mm

    @property
    def D_i_mm(self):
        return self.internal_diameter_mm

    @property
    def L(self):
        return self.cylindrical_shell_length_mm

    @property
    def L_mm(self):
        return self.cylindrical_shell_length_mm

    @property
    def P_design_bar(self):
        return self.design_pressure_bar

    @property
    def P_design_MPa(self):
        """Convert design pressure to MPa (N/mm^2)"""
        return self.P_design_bar / 10.0

    @property
    def T_design_C(self):
        return self.design_temperature_c


# Define a type for the calculation output
class DesignResult(TypedDict):
    e_shell_required_mm: float
    e_head_required_mm: float
    e_nominal_mm: float


def calculate_shell_thickness(params: VesselParameters) -> float:
    """Calculates the minimum required thickness for the cylindrical shell."""
    P = params.P_design_MPa
    D_i = params.D_i
    f = params.f
    z = params.z
    c = params.c

    # Formula: e = (P * D_i) / (2 * f * z - P)
    denominator = 2 * f * z - P
    if denominator <= 0:
        raise ValueError("Shell denominator is non-positive.")

    e_min = (P * D_i) / denominator
    e_req = e_min + c
    return e_req


def calculate_klöpper_head_thickness(params: VesselParameters) -> float:
    """Calculates the minimum required thickness for the torispherical head."""
    P = params.P_design_MPa
    f = params.f
    z = params.z
    c = params.c
    R_i = params.R_i
    r_i = params.r_i

    # 1. Stress-concentration factor (M) for torispherical heads (EN 13445-3, Cl. 8.4.3.2)
    M = 0.25 * (3 + np.sqrt(R_i / r_i))

    # 2. Formula: e = (P * R_i * M) / (2 * f * z - P * (M - 1))
    denominator = 2 * f * z - P * (M - 1)
    if denominator <= 0:
        raise ValueError("Head denominator is non-positive.")

    e_min = (P * R_i * M) / denominator
    e_req = e_min + c
    return e_req


def perform_vessel_design(params: VesselParameters) -> DesignResult:
    """Performs all required calculations and determines the nominal thickness."""
    e_shell = calculate_shell_thickness(params)
    e_head = calculate_klöpper_head_thickness(params)

    e_required_max = max(e_shell, e_head)

    # Round up to the next commercially available 0.5 mm thickness
    e_nominal = np.ceil(e_required_max / 0.5) * 0.5

    return {
        "e_shell_required_mm": float(f"{e_shell:.2f}"),
        "e_head_required_mm": float(f"{e_head:.2f}"),
        "e_nominal_mm": float(f"{e_nominal:.1f}"),
    }


if __name__ == "__main__":
    main()
