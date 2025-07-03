# Load libraries
library(ggplot2)
library(dplyr)
library(readr)
library(lubridate)
library(tidyr)

# --------------- Nitrate over time

df <- read_csv('/Users/Administrator/Documents/University/Year 3/2b/Thesis/Bachelor-Thesis/data/aligned/merged_dataset_1.csv')

# Drop rows with missing values
df_clean <- df %>% drop_na()

# Parse date column (named 'date') and extract year
df_clean <- df_clean %>%
  mutate(date = ymd_hms(date),
         Year = year(date))
# Group and calculate average nitrate
yearly_nitrate <- df_clean %>%
  group_by(Year) %>%
  summarise(MeanNitrate = mean(nitrate, na.rm = TRUE))

# Determine range of years
year_range <- range(yearly_nitrate$Year, na.rm = TRUE)

# Group by year and calculate average nitrate
yearly_nitrate <- df_clean %>%
  group_by(Year) %>%
  summarise(MeanNitrate = mean(nitrate, na.rm = TRUE))

ggplot(yearly_nitrate, aes(x = Year, y = MeanNitrate)) +
  geom_line(color = "black", linewidth = 1.1) +
  scale_x_continuous(breaks = seq(year_range[1], year_range[2], by = 2)) +
  labs(
    title = NULL,
    x = "Year",
    y = "Nitrate (mg/L)"
  ) +
  theme_minimal(base_family = "STIXTwoText_Medium") +
  theme(
    text = element_text(size = 20),
    axis.text = element_text(size = 20),
    axis.title.y = element_text(margin = margin(r = 10))
  )

# --------------- Histogram

# Load the dataset
df <- read_csv('/Users/Administrator/Documents/University/Year 3/2b/Thesis/Bachelor-Thesis/data/aligned/merged_dataset_1.csv')

# Remove rows with missing nitrate values
df_clean <- na.omit(df)

# Plot histogram
ggplot(df_clean, aes(x = nitrate)) +
  geom_histogram(binwidth = 2.5, fill = "darkgray", color = "black") +
  labs(
    title = NULL,
    x = "Nitrate (mg/L)",
    y = "Frequency"
  ) +
  theme_minimal(base_family = "STIXTwoText_Medium") +
  theme(
    text = element_text(size = 16),
    axis.text = element_text(size = 20),
    axis.title = element_text(size = 20),
    axis.title.y = element_text(margin = margin(r = 10)),
    panel.grid.minor.y = element_blank()
  )

# --------------- Density

# Load your dataset
data <- read.csv('/Users/Administrator/Documents/University/Year 3/2b/Thesis/Bachelor-Thesis/data/aligned/merged_dataset_1.csv')
data <- na.omit(data)

# Convert nitrate to numeric (if needed)
data$nitrate <- as.numeric(data$nitrate)
data <- data[is.finite(data$nitrate), ]

#data$log_nitrate <- log(data$nitrate)

ggplot(data, aes(x = nitrate)) +
  geom_density(fill = "black", alpha = 0.8) +
  labs(
    title = NULL,
    x = "Log Nitrate",
    y = NULL
  ) +
  theme_minimal(base_family = "STIXTwoText_Medium", base_size = 20) +
  theme(
    axis.title.x = element_text(size = 16, family = "STIXTwoText_Medium")
  )

max(data$nitrate, na.rm = TRUE)

# "Nitrate Concentration Density"



library(patchwork)

p1 <- ggplot(data, aes(x = nitrate)) +
  geom_density(fill = "black") +
  xlim(0, 10) +
  labs(title = "Zoomed in (0–10)") +
  theme_minimal()

p2 <- ggplot(data, aes(x = nitrate)) +
  geom_density(fill = "black") +
  labs(title = "Full range") +
  theme_minimal()

p1
p2
