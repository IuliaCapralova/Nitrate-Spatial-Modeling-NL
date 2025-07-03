library(ggplot2)
library(dplyr)
library(showtext)
library(ggcorrplot)

data <- read.csv('/Users/Administrator/Documents/University/Year 3/2b/Thesis/Bachelor-Thesis/data/aligned/merged_dataset_1.csv')%>%
  drop_na() %>%
  mutate(across(everything(), as.numeric))

# Select only the desired columns
selected_data <- data %>% select(
  nitrate, population, `groundwater.depth`, elevation, precipitation,temperature, `n.deposition`, organicmattercontent_1, density_1, acidity_1
)

# Compute correlation matrix
corr_matrix <- cor(selected_data, use = "complete.obs", method = "pearson")

# Plot the correlation map
ggcorrplot(corr_matrix,
           #type = "lower",
           lab = TRUE,
           lab_size = 4,
           method = "square",
           colors = c("black", "white", "black"),
           title = "",
           ggtheme = theme_minimal())+
           theme(
              axis.text.x = element_text(size = 16, angle = 45, hjust = 1),
              axis.text.y = element_text(size = 16)
            )

corr_matrix_abs <- abs(corr_matrix)

# Plot
p <- ggcorrplot(corr_matrix_abs,
                lab = FALSE,
                method = "square",
                colors = c("white", "black"),
                ggtheme = theme_minimal(base_size = 14)) +
  scale_fill_gradient(
    low = "white",
    high = "black",
    limits = c(0, 1),           # Ensure range is 0 to 1
    name = "Correlation"
  ) +
  theme(
    axis.text.x = element_text(size = 16, angle = 45, hjust = 1),
    axis.text.y = element_text(size = 16),
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12),
    legend.key.height = unit(nrow(corr_matrix_abs), "lines")  # match heatmap height
  )

print(p)







