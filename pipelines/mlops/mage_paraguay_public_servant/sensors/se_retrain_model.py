
@sensor
def check_condition(
    
    
    
    
    **kwargs
) -> bool, int:
    
   code, df_actual_ds, df_last_ds = data_set_encoder
   retrain = False
   if code != 0:
        retrain = generate_report_evidently(df_actual_ds, df_last_ds)

   return retrain, code