import React from 'react';
import { BookOpen, Database, Activity, Flame, CloudRain, Car, Thermometer, GitBranch } from 'lucide-react';
import './ResearchMethodology.css';

const ResearchMethodology = () => {
  return (
    <div className="container research-page">
      <header className="research-header">
        <BookOpen size={40} className="header-icon" />
        <h1>Research & Methodology</h1>
        <p className="subtitle">
          GaiaOS is designed as a multi-domain Earth intelligence system that integrates satellite imagery, atmospheric observations, and geospatial datasets to produce predictive insights across environmental and urban systems. The platform combines machine learning models with large-scale geospatial data pipelines to forecast environmental risks and structural changes across multiple domains.
        </p>
        <p className="subtitle">
          The system is composed of five specialized modules, each designed to model a specific Earth system process. These modules share common data sources and preprocessing pipelines, enabling cross-domain analysis and integrated predictions.
        </p>
      </header>

      <div className="module-list">
        
        {/* Module 1 */}
        <section className="research-module glass-panel">
          <div className="module-content">
            <div className="module-text">
              <div className="module-title mb-4">
                <CloudRain size={28} className="icon-flood" />
                <h2>Module 1 — Flood Probability Prediction</h2>
              </div>
              <p>
                The flood prediction module estimates the likelihood of flooding across geographic regions within the next seventy-two hours. The model integrates hydrological, meteorological, and terrain data to generate spatial flood probability maps.
              </p>
              <p>
                The prediction pipeline begins with rainfall observations, soil moisture levels, river discharge measurements, and terrain elevation models. These variables provide a representation of both current environmental conditions and the physical characteristics that influence water flow and accumulation.
              </p>
              <p>
                The first version of the model uses a gradient-boosted decision tree architecture to estimate flood probability based on tabular environmental variables. The upgraded system introduces a temporal deep learning approach using a convolutional recurrent network that processes sequences of rainfall grids. In this formulation, rainfall patterns are treated as a series of spatial frames over time, allowing the model to learn the evolution of precipitation systems and their relationship to flooding events.
              </p>
              <p>
                Users interact with this module through the map interface by selecting administrative districts or drawing custom regions. The system returns a probabilistic risk score, identifies the primary environmental drivers contributing to the risk level, and visualizes the temporal evolution of flood probability across the forecast horizon.
              </p>
              <p>
                Datasets used for this module include ERA5 precipitation data from Copernicus, SMAP soil moisture measurements from NASA, terrain elevation models from the Shuttle Radar Topography Mission, radar imagery from the Sentinel-1 satellite, river discharge records from the Global Flood Awareness System, and historical flood records from the India Meteorological Department.
              </p>
            </div>
            
            <div className="module-visuals">
              <div className="model-diagram glass-panel-heavy">
                <h4><GitBranch size={16} /> AI Architecture Pipeline</h4>
                <div className="diagram-flow">
                  <div className="flow-box">Rainfall Data</div>
                  <div className="flow-box">Soil Moisture</div>
                  <div className="flow-box">River Level</div>
                  <div className="flow-box">Terrain Elevation</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box highlight">Flood Prediction Model</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box result">Flood Probability Map</div>
                </div>
              </div>
              <img src="/flood_prediction_concept_1773467258283.png" alt="Flood Prediction Concept" className="module-image" />
            </div>
          </div>
        </section>

        {/* Module 2 */}
        <section className="research-module glass-panel">
          <div className="module-content reverse">
            <div className="module-text">
              <div className="module-title mb-4">
                <Thermometer size={28} className="icon-climate" />
                <h2>Module 2 — Climate Pattern Forecasting</h2>
              </div>
              <p>
                The climate prediction module estimates regional atmospheric conditions up to thirty days in advance. The model predicts temperature anomalies relative to long-term climatological averages, estimates the expected arrival timing of the monsoon season, and evaluates the probability of drought development.
              </p>
              <p>
                The model architecture is based on a transformer-based neural network designed for spatiotemporal atmospheric data. The network is trained on multi-level atmospheric reanalysis datasets spanning several decades. By learning large-scale circulation patterns across pressure levels, the model captures precursor signals that often precede extreme heat events, delayed rainfall patterns, or seasonal drought development.
              </p>
              <p>
                Users interact with the module by selecting a location on the map or searching for a region. The interface then presents the expected temperature anomaly, seasonal rainfall outlook, and drought indicators derived from atmospheric patterns.
              </p>
              <p>
                The datasets used include ERA5 multi-level atmospheric reanalysis data containing temperature, wind velocity, humidity, and geopotential height fields. Additional predictors include global sea surface temperature observations from NOAA, historical monsoon onset records from the India Meteorological Department, and rainfall observations from the CHIRPS precipitation dataset.
              </p>
            </div>
            
            <div className="module-visuals">
              <div className="model-diagram glass-panel-heavy">
                <h4><GitBranch size={16} /> AI Architecture Pipeline</h4>
                <div className="diagram-flow">
                  <div className="flow-box">Atmospheric Data</div>
                  <div className="flow-box">Wind Fields</div>
                  <div className="flow-box">Humidity</div>
                  <div className="flow-box">Sea Surface Temperature</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box highlight">Climate Transformer Model</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box result">30-Day Climate Forecast</div>
                </div>
              </div>
              <img src="/climate_simulation_map_1773467273867.png" alt="Climate Patterns Concept" className="module-image" />
            </div>
          </div>
        </section>

        {/* Module 3 */}
        <section className="research-module glass-panel">
          <div className="module-content">
            <div className="module-text">
              <div className="module-title mb-4">
                <Activity size={28} className="icon-crop" />
                <h2>Module 3 — Crop Yield Forecasting</h2>
              </div>
              <p>
                The crop prediction module estimates agricultural yield several weeks prior to harvest. The model integrates satellite vegetation signals with environmental conditions to predict whether crop production will exceed or fall below historical averages.
              </p>
              <p>
                The system analyzes vegetation health using satellite-derived normalized difference vegetation index (NDVI) measurements. NDVI provides a quantitative measure of plant greenness and photosynthetic activity, which correlates strongly with crop productivity during the growing season.
              </p>
              <p>
                The model architecture combines two complementary learning systems. A temporal convolutional network processes weekly NDVI observations as a time series to capture seasonal vegetation dynamics. In parallel, a gradient-boosted model analyzes tabular environmental features such as rainfall, soil moisture, and seasonal climate indicators. The predictions from both models are combined to generate the final yield forecast.
              </p>
              <p>
                When users select a district and choose a crop type, the system presents the predicted production level, a confidence interval representing forecast uncertainty, and a historical comparison of vegetation signals.
              </p>
              <p>
                This module relies on several datasets including MODIS satellite NDVI measurements, SMAP soil moisture observations, district-level crop production statistics collected by ICRISAT, rainfall data from the India Meteorological Department, and crop growth calendars published by the Food and Agriculture Organization.
              </p>
            </div>
            
            <div className="module-visuals">
              <div className="model-diagram glass-panel-heavy">
                <h4><GitBranch size={16} /> AI Architecture Pipeline</h4>
                <div className="diagram-flow">
                  <div className="flow-box">Satellite NDVI</div>
                  <div className="flow-box">Rainfall Data</div>
                  <div className="flow-box">Soil Moisture</div>
                  <div className="flow-box">Temperature</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box highlight">Crop Yield Prediction Model</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box result">Yield Forecast Map</div>
                </div>
              </div>
              <img src="/crop_yield_ndvi_1773467305923.png" alt="Crop Yield Concept" className="module-image" />
            </div>
          </div>
        </section>

        {/* Module 4 */}
        <section className="research-module glass-panel">
          <div className="module-content reverse">
            <div className="module-text">
              <div className="module-title mb-4">
                <Flame size={28} className="icon-wildfire" />
                <h2>Module 4 — Wildfire Risk Assessment</h2>
              </div>
              <p>
                The wildfire prediction module evaluates short-term fire danger across forest and agricultural landscapes. The system produces spatial risk maps describing the probability of fire ignition and spread over the coming week.
              </p>
              <p>
                The model analyzes meteorological conditions that influence fire behavior, including temperature, humidity, and wind speed. These atmospheric variables are combined with vegetation indicators that measure fuel availability and dryness.
              </p>
              <p>
                The primary model is an ensemble gradient boosting system trained on historical fire occurrence data. In addition, a convolutional neural network analyzes vegetation and land cover maps to identify areas where combustible fuel loads are accumulating.
              </p>
              <p>
                Users can select a region on the map to view the predicted fire danger category along with the environmental variables contributing to the risk level. Historical fire activity is also displayed to provide context for the prediction.
              </p>
              <p>
                The wildfire module uses fire detection records from the NASA FIRMS system, atmospheric observations from ERA5, burned area datasets derived from MODIS satellite imagery, terrain slope models from SRTM, and global vegetation fuel classifications provided by the Copernicus land monitoring service.
              </p>
            </div>
            
            <div className="module-visuals">
              <div className="model-diagram glass-panel-heavy">
                <h4><GitBranch size={16} /> AI Architecture Pipeline</h4>
                <div className="diagram-flow">
                  <div className="flow-box">Temperature</div>
                  <div className="flow-box">Wind Speed</div>
                  <div className="flow-box">Humidity</div>
                  <div className="flow-box">Vegetation Dryness</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box highlight">Wildfire Risk Model</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box result">Fire Danger Map</div>
                </div>
              </div>
              <img src="/wildfire_risk_map_1773467328902.png" alt="Wildfire Risk Concept" className="module-image" />
            </div>
          </div>
        </section>

        {/* Module 5 */}
        <section className="research-module glass-panel">
          <div className="module-content">
            <div className="module-text">
              <div className="module-title mb-4">
                <Car size={28} className="icon-traffic" />
                <h2>Module 5 — Traffic and Urban Growth Modeling</h2>
              </div>
              <p>
                The urban systems module addresses two related processes: long-term urban expansion and short-term traffic congestion.
              </p>
              <p>
                Urban growth is modeled using satellite imagery to detect land-use change over time. A deep convolutional segmentation network analyzes multi-year satellite observations and identifies areas where agricultural or natural landscapes are being converted into urban development. This model produces spatial projections indicating where future urban expansion is likely to occur.
              </p>
              <p>
                Traffic forecasting is performed using a graph-based neural network that represents road networks as interconnected nodes and edges. Traffic flow dynamics are learned from historical congestion patterns and spatial road connectivity. The system predicts which transportation corridors are likely to experience congestion during different times of day.
              </p>
              <p>
                Users can select a city on the map to visualize projected urban growth zones and predicted traffic congestion patterns.
              </p>
              <p>
                The datasets used for this module include Sentinel-2 multispectral satellite imagery, road network data from OpenStreetMap, population density estimates from the Meta High Resolution Settlement Layer dataset, night-time illumination observations from the VIIRS satellite, and urban land cover maps from the Global Human Settlement Layer.
              </p>
            </div>
            
            <div className="module-visuals">
              <div className="model-diagram glass-panel-heavy">
                <h4><GitBranch size={16} /> AI Architecture Pipeline</h4>
                <div className="diagram-flow">
                  <div className="flow-box">Satellite Imagery</div>
                  <div className="flow-box">Population Density</div>
                  <div className="flow-box">Road Network</div>
                  <div className="flow-box">Night Light Data</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box highlight">Urban Growth & Traffic Model</div>
                  <div className="flow-arrow">↓</div>
                  <div className="flow-box result">City Expansion + Congestion Map</div>
                </div>
              </div>
              <img src="/urban_traffic_growth_1773467344709.png" alt="Urban Growth Concept" className="module-image" />
            </div>
          </div>
        </section>

      </div>

      {/* Shared Infrastructure & Evaluation sections */}
      <div className="infra-grid">
        <section className="shared-infra glass-panel">
          <div className="card-top">
            <Database size={28} className="icon-db" />
            <h2>Shared Data Infrastructure & Pipelines</h2>
          </div>
          <div className="card-content">
            <p>
              All modules rely on a common geospatial data infrastructure that integrates atmospheric observations, satellite imagery, terrain models, and socio-environmental datasets. These datasets are obtained from publicly accessible scientific repositories maintained by international space agencies, meteorological institutions, and environmental monitoring programs.
            </p>
            <p>
              The primary atmospheric dataset used across the system is ERA5 reanalysis, which provides hourly global weather data spanning multiple decades. Additional supporting datasets include rainfall records from the India Meteorological Department, satellite observations from MODIS and Sentinel missions, soil moisture measurements from SMAP, and terrain elevation models from the Shuttle Radar Topography Mission.
            </p>
            <h4>Data Processing and Machine Learning Pipeline</h4>
            <p>
              The GaiaOS system processes large volumes of geospatial data using specialized scientific computing libraries designed for satellite imagery and climate datasets. Data ingestion pipelines transform raw satellite observations and atmospheric fields into spatial grids that can be consumed by machine learning models.
            </p>
            <p>
              Geospatial analysis tools are used to align datasets with different coordinate systems, resolutions, and temporal frequencies. Machine learning models are trained using both tabular and spatial data representations depending on the prediction task. Deep learning architectures are used for satellite imagery analysis and spatiotemporal prediction tasks, while ensemble tree-based methods are applied to structured environmental datasets.
            </p>
          </div>
        </section>

        <div className="col-split">
          <section className="evaluation-box glass-panel-heavy">
            <h2>Model Evaluation</h2>
            <p>
              Each module is evaluated using independent test datasets representing historical environmental events. The performance of the models is measured using established evaluation metrics including area under the ROC curve, precision and recall for event detection, and classification skill scores used in meteorological forecasting.
            </p>
            <p>
              Model predictions are also compared against baseline approaches such as persistence forecasts and operational predictions published by national meteorological agencies. This comparison ensures that the models provide measurable improvements over simpler prediction methods.
            </p>
          </section>

          <section className="integration-box glass-panel-heavy">
            <h2>System Integration</h2>
            <p>
              The outputs from all five modules are integrated into a unified geospatial interface where users can explore predictions interactively. The system allows users to analyze predictions for administrative regions or custom geographic areas defined directly on the map.
            </p>
            <p>
              The combination of multiple predictive systems allows GaiaOS to reveal relationships between environmental processes such as climate variability, vegetation health, wildfire risk, and urban development.
            </p>
          </section>
        </div>
      </div>

    </div>
  );
};

export default ResearchMethodology;
