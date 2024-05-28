```mermaid
classDiagram
    Standard *-- SignalType
    Standard *-- Sample
    Standard *-- CalibrationModel
    CalibrationModel *-- CalibrationRange
    CalibrationModel *-- FitStatistics
    CalibrationModel *-- Parameter
    
    class Standard {
        +string name*
        +float ph*
        +float temperature*
        +str temperature_unit*
        +float wavelength
        +SignalType signal_type
        +Sample[0..*] samples
        +datetime created
        +datetime modified
        +CalibrationModel calibration_result
    }
    
    class Sample {
        +string species_id*
        +float concentration*
        +str unit*
        +float signal*
    }
    
    class CalibrationModel {
        +string name*
        +string signal_law*
        +Parameter[0..*] parameters
        +boolean was_fitted
        +CalibrationRange calibration_range
        +FitStatistics statistics
    }
    
    class CalibrationRange {
        +float conc_lower
        +float conc_upper
        +float signal_lower
        +float signal_upper
    }
    
    class FitStatistics {
        +float aic
        +float bic
        +float r2
        +float rmsd
    }
    
    class Parameter {
        +string name
        +float value
        +float init_value
        +float stderr
        +float lower_bound
        +float upper_bound
    }
    
    class SignalType {
        << Enumeration >>
        +ABSORBANCE
        +TRANSMITTANCE
        +REFLECTANCE
    }
    
```