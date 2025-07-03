library(forecast)
library(ggplot2)

# Number of observations
n <- nrow(data)
  > 
    > # Compute ACF of temperature
    > acf_obj <- Acf(data$temp_mean, lag.max = 80, plot = FALSE)
    > acf_vals <- as.numeric(acf_obj$acf)
    > lags <- as.numeric(acf_obj$lag)
    > 
      > # Bartlett’s formula: compute CI bounds
      > var_rho <- sapply(1:length(lags), function(k) {
        +     if (k == 1) return(1 / n)
        +     if (k == 2) return(1 / n)
        +     1 / n * (1 + 2 * sum(acf_vals[2:(k - 1)]^2))
        + })
      > ci_bounds <- 1.96 * sqrt(var_rho)
      > 
        > # Build ACF data frame (every 3rd lag only)
        > df_acf <- data.frame(
          +     lag = lags,
          +     acf = acf_vals,
          +     ci = ci_bounds
          + )
        > df_acf <- df_acf[df_acf$lag %% 3 == 0, ]
        > 
          > # Plot
          > ggplot(df_acf, aes(x = lag, y = acf)) +
          +     geom_bar(stat = "identity", fill = "black", width = 0.6) +
          +     geom_line(aes(y = ci), linetype = "dashed", color = "darkred") +
          +     geom_line(aes(y = -ci), linetype = "dashed", color = "darkred") +
          +     geom_hline(yintercept = 0, color = "gray40") +
          +     scale_y_continuous(breaks = c(-1, -0.5, 0.0, 0.5, 1.0)) +
          +     theme_minimal(base_family = "STIXTwoText_Medium") +
          +     labs(
            +         title = NULL,
            +         x = "Lag (in days)", y = NULL
            +     ) +
          +     theme(
            +         axis.text = element_text(size = 18),
            +         axis.title = element_text(size = 18),
            +         text = element_text(size = 18)
            +     )