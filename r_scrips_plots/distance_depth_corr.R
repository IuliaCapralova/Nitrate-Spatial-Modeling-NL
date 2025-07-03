library(forecast)
library(ggplot2)
library(dplyr)
library(sf)
library(tidyr)
library(stats)
library(geosphere)

# Load data
file_path <- '/Users/Administrator/Documents/University/Year 3/2b/Thesis/Bachelor-Thesis/data/clean/well_depth_data/for_Alignment/zuid-holland_well_depth_combined_1.csv'
df <- read.csv(file_path)

# Convert to sf
df_sf <- st_as_sf(df, wkt = "geometry", crs = 4326)
df_sf <- st_transform(df_sf, crs = 3857)  # Project to meters

# Get one location per well
well_locations <- df_sf %>%
  group_by(Well_ID) %>%
  summarise(geometry = first(geometry)) %>%
  st_as_sf()

# Pivot data: Date × Well_ID → Depth
df$Date <- as.Date(df$Date)
depth_ts <- df %>%
  select(Date, Well_ID, Depth) %>%
  pivot_wider(names_from = Well_ID, values_from = Depth)

# Remove wells with >50% missing data
min_obs <- nrow(depth_ts) * 0.5
depth_ts <- depth_ts %>%
  select(where(~ sum(!is.na(.)) >= min_obs))

# Extract well names and coordinates
valid_wells <- names(depth_ts)[-1]
coords <- st_coordinates(well_locations[match(valid_wells, well_locations$Well_ID), ])

# Compute pairwise correlations and distances
cor_matrix <- cor(depth_ts[,-1], use = "pairwise.complete.obs")
dist_matrix <- dist(coords)

# Extract upper triangle
get_upper_tri <- function(mat) {
  mat[lower.tri(mat, diag = TRUE)] <- NA
  return(mat)
}

cor_vals <- get_upper_tri(cor_matrix) %>% as.vector()
dist_vals <- get_upper_tri(as.matrix(dist_matrix)) %>% as.vector()

# Combine into dataframe and filter
df_corr <- data.frame(
  Distance = dist_vals,
  Correlation = cor_vals
) %>% 
  drop_na() %>%
  filter(Distance <= 20000)

# Lowess smoothing
df_corr$Distance_km <- df_corr$Distance / 1000
smooth_vals_km <- lowess(df_corr$Distance_km, df_corr$Correlation, f = 0.3)
# smooth_vals <- lowess(df_corr$Distance, df_corr$Correlation, f = 0.3)

ggplot(df_corr, aes(x = Distance_km, y = Correlation)) +
  geom_point(alpha = 0.2, color = "gray50", size = 1) +
  geom_line(data = as.data.frame(smooth_vals_km), aes(x = x, y = y), color = "black", linewidth = 1.3) +
  theme_minimal(base_family = "Helvetica") +
  labs(
    title = NULL,
    x = "Distance (m)",
    y = NULL
  ) +
  theme(
    axis.text = element_text(size = 18),
    axis.title = element_text(size = 18),
    legend.position = "none"
  )


