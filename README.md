# 🏗️ EN 13445 Pressure Vessel Design Calculator (Python)

A modular and highly reliable **Python library** for performing preliminary wall thickness calculations for unfired pressure vessels.

This tool is designed for **Chemical and Mechanical Engineers** to quickly assess the required wall thickness for cylindrical shells and **Klöpper (Torispherical) heads** under internal pressure, using the principles of the European standard **EN 13445-3**.

---

## ✨ Key Features

* **EN 13445 Compliance:** Calculations adhere to the fundamental formulas for shell and torispherical head design.
* **Pydantic Validation:** Ensures all design inputs (Pressure, Temperature, Dimensions) are strictly validated before computation.
* **Functional Design:** Separates the data model (`VesselParameters`) from the pure calculation logic for enhanced testability and maintainability.
* **Stainless Steel Focus:** Uses common material properties for high-quality stainless steel (e.g., **1.4404** / 316L).

---

## 🛠️ Installation

This project requires `numpy` for mathematical operations and `pydantic` for data validation.

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    cd [YOUR_REPO_NAME]
    ```

2.  **Install dependencies:**
    ```bash
    pip install numpy pydantic
    ```
    *(Note: Ensure your Python environment is running Python 3.9+ for `StrEnum` support.)*

---

## 🚀 Usage Example

The core functionality is accessed by defining the inputs in the `VesselParameters` model and passing the resulting object to the `perform_vessel_design` function.

### `vessel.py`

*(Assuming the calculation and model definitions are in this file)*

```python
from vessel import VesselParameters, perform_vessel_design 
# Replace 'your_module' with the actual file/module name

def main_example():
    print("Starting Pressure Vessel Calculation...")
    
    # Define Inputs: 1.2m Diameter, 3m Length, 3 bar, 100°C
    design_inputs = {
        "D_i": 1200,
        "L": 3000,
        "P_design_bar": 3.0,
        "T_design_C": 100.0,
        # "material_grade": MaterialGrade._1_4404 is the default
    }

    try:
        # 1. Validate and prepare parameters
        params = VesselParameters(**design_inputs)
        
        # 2. Run the calculation
        results = perform_vessel_design(params)
        
        # 3. Output
        print("\n--- Final Design Results (EN 13445) ---")
        print(f"Design Stress (f): {params.f} MPa")
        print(f"Required Shell Thickness: {results.e_shell_required_mm} mm")
        print(f"Required Head Thickness: {results.e_head_required_mm} mm")
        print(f"\n**Recommended Nominal Thickness:** {results.e_nominal_mm} mm")
        
    except Exception as e:
        print(f"An error occurred during design: {e}")

if __name__ == "__main__":
    main_example()