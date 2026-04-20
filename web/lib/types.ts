export interface OverallSummary {
  model: string;
  mae: number;
  rmse: number;
  mape: number;
  smape: number;
  mase: number;
  coverage: number;
  avg_width: number;
  pinball_lower: number;
  pinball_upper: number;
  calibration_error: number;
}

export interface HorizonSummary {
  model: string;
  horizon_step: number;
  mae: number;
  rmse: number;
  mape: number;
  smape: number;
  mase: number;
  coverage: number;
  avg_width: number;
  calibration_error: number;
}

export interface ResultsFile {
  meta: {
    series_name: string;
    n_obs: number;
    horizon: number;
    initial_train: number;
    step: number;
    mode: string;
    alpha: number;
    seasonality: number;
    models: string[];
    n_folds: number;
    conformal: boolean;
    calibration_folds: number;
  };
  overall: OverallSummary[];
  horizons: HorizonSummary[];
  rolling_coverage: Record<string, Array<number | null>>;
}

export interface RecordRow {
  model: string;
  fold: number;
  horizon_step: number;
  train_end: string;
  test_time: string;
  y_true: number;
  y_pred: number;
  lower: number;
  upper: number;
  sigma: number;
}
