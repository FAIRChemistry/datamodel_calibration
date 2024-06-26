```mermaid
classDiagram
    Standard *-- SignalType
    Standard *-- Sample
    Standard *-- CalibrationModel
    CalibrationModel *-- CalibrationRange
    CalibrationModel *-- FitStatistics
    CalibrationModel *-- Parameter
    
    class Standard {
        +string molecule_id*
        +string molecule_symbol*
        +float ph*
        +float temperature*
        +str temp_unit*
        +float wavelength
        +string molecule_name
        +SignalType signal_type
        +Sample[0..*] samples
        +datetime created
        +CalibrationModel result
    }
    
    class Sample {
        +float concentration*
        +str conc_unit*
        +float signal*
    }
    
    class CalibrationModel {
        +string name*
        +string molecule_id
        +string signal_law
        +Parameter[0..*] parameters
        +string molecule_symbol
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
        +string symbol
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