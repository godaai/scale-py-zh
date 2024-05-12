library(ggplot2)
library(cowplot)


## plot1
df <- data.frame(xx=seq(0, 10, 0.05))

# observation and objective function
y.true <- c(7.5, 6.8, 7.0, 4.25, 3.75, 6.0)
y.predict <- c(7.8, 6.8, 8.0, 6.8, 3.75, 3.85, 5.15, 7.5)

df$y.true <- splinefun(x=seq(0, 10, 2), y.true)(df$xx)
df$y.predict <- splinefun(x=c(seq(0, 8, 2), 8.5, 9, 10), y.predict)(df$xx)

# confidence interval
# lower bound
x.lci.1 <- seq(0, 2, 0.05)
y.lci.1 <- splinefun(x=c(0, 1, 1.5, 2),
                     y=c(6.4, 6.35, 6.45, 6.8))(x.lci.1)

x.lci.2 <- seq(2, 8, 0.05)
y.lci.2 <- splinefun(x=c(2, 2.2, 3, 4, 6, 8),
                     y=c(6.8, 6.65, 6.45, 5.4, 3.15, 3.75))(x.lci.2)

x.lci.3 <- seq(8, 10, 0.05)
y.lci.3 <- splinefun(x=c(8, 8.5, 9.5, 10),
                     y=c(3.75, 3.55, 4.3, 5.0))(x.lci.3)

temp.df <- data.frame(x.lci=c(x.lci.1, x.lci.2, x.lci.3), 
                      y.lci=c(y.lci.1, y.lci.2, y.lci.3))
temp.df <- temp.df[!duplicated(temp.df$x.lci), ]

df$y.lci <- NULL
df$y.lci[which(abs(df$xx-temp.df$x.lci)<0.01)] <- temp.df$y.lci

# upper bound
x.uci.1 <- seq(0, 2, 0.05)
y.uci.1 <- splinefun(x=c(0, 1, 1.5, 2),
                     y=c(8.5, 7.5, 7.0, 6.8))(x.uci.1)

x.uci.2 <- seq(2, 8, 0.05)
y.uci.2 <- splinefun(x=c(2, 3, 4, 6, 6.5, 7.5, 8),
                     y=c(6.8, 7.8, 8.15, 6.0, 5.3, 4.0, 3.75))(x.uci.2)

x.uci.3 <- seq(8, 10, 0.05)
y.uci.3 <- splinefun(x=c(8, 8.5, 9.5, 10),
                     y=c(3.75, 4.85, 6.2, 7.0))(x.uci.3)

temp.df <- data.frame(x.uci=c(x.uci.1, x.uci.2, x.uci.3), 
                      y.uci=c(y.uci.1, y.uci.2, y.uci.3))
temp.df <- temp.df[!duplicated(temp.df$x.uci), ]

df$y.uci <- NULL
df$y.uci[which(abs(df$xx-temp.df$x.uci)<0.01)] <- temp.df$y.uci

# other curves
x.o.1 <- seq(0, 8, 0.05)
y.o.1 <- splinefun(x=seq(0, 8, 1),
                     y=c(0, 0, 0, 0.01, 0.03, 0.2, 0.8, 1.2, 0))(x.o.1)

x.o.2 <- seq(8, 10, 0.05)
y.o.2 <- splinefun(x=c(8, 8.5, 9, 9.5, 10),
                   y=c(0, 1, 0.75, 0.6, 0.5))(x.o.2)

temp.df <- data.frame(x.o=c(x.o.1, x.o.2), 
                      y.o=c(y.o.1, y.o.2))
temp.df <- temp.df[!duplicated(temp.df$x.o), ]

df$y.o <- NULL
df$y.o[which(abs(df$xx-temp.df$x.o)<0.01)] <- temp.df$y.o
df$y.o[which(df$y.o<0.01)] <- 0.01



p1 <- ggplot(df, aes(x = xx)) + 
  theme(
    panel.background = element_rect(fill = "white", color = "black"),  # 设置透明背景和图形边框
    panel.grid.major = element_blank(),  # 不显示网格线
    panel.grid.minor = element_blank(),  # 不显示网格线
    axis.title = element_blank(),  # 不显示坐标轴标签
    axis.text = element_blank(),  # 不显示坐标轴刻度
    axis.ticks = element_blank(), # 不显示坐标轴刻度线
    plot.margin = margin(t = 0.3, r = 0, b = 0, l = 0, unit = "inch")
  ) +
  scale_x_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) +  
  scale_y_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) + 
  geom_ribbon(aes(ymin = y.lci, ymax = y.uci), fill = "#d1e8ff") +
  geom_line(aes(y = y.true), color = "black") + 
  geom_line(aes(y = y.predict), color = "black", linetype = "dashed") + 
  # geom_line(aes(y = y.lci), color = "blue") + 
  # geom_line(aes(y = y.uci), color = "blue") + 
  geom_line(aes(y = y.o), color = "orange") +
  geom_ribbon(aes(ymin = 0, ymax = y.o), fill = "#fff4e0")



## plot2
df <- data.frame(xx=seq(0, 10, 0.05))

# observation and objective function
y.true <- c(7.5, 6.8, 7.2, 7.2, 3.75, 6.0, 5.6)
y.predict <- c(7.8, 6.8, 7.25, 7.7, 7.8, 7.25, 5.6, 3.75, 3.85, 5.15, 7.7)

df$y.true <- splinefun(x=c(seq(0, 10, 2), 7), y.true)(df$xx)
df$y.predict <- splinefun(x=c(seq(0, 4, 2), 5, 6, 6.5, 7, 8, 8.5, 9, 10), y.predict)(df$xx)

# confidence interval
# lower bound
x.lci.1 <- seq(0, 2, 0.05)
y.lci.1 <- splinefun(x=c(0, 1, 1.5, 2),
                     y=c(6.4, 6.35, 6.45, 6.8))(x.lci.1)

x.lci.2 <- seq(2, 7, 0.05)
y.lci.2 <- splinefun(x=c(2, 2.2, 3, 4, 6, 7),
                     y=c(6.8, 6.5, 6.4, 6.5, 6.5, 5.6))(x.lci.2)

x.lci.3 <- seq(7, 8, 0.05)
y.lci.3 <- splinefun(x=c(7, 7.5, 8),
                     y=c(5.6, 4.5, 3.75))(x.lci.3)

x.lci.4 <- seq(8, 10, 0.05)
y.lci.4 <- splinefun(x=c(8, 8.5, 9.5, 10),
                     y=c(3.75, 3.1, 3.3, 4.4))(x.lci.4)

temp.df <- data.frame(x.lci=c(x.lci.1, x.lci.2, x.lci.3, x.lci.4), 
                      y.lci=c(y.lci.1, y.lci.2, y.lci.3, y.lci.4))
temp.df <- temp.df[!duplicated(temp.df$x.lci), ]

df$y.lci <- NULL
df$y.lci[which(abs(df$xx-temp.df$x.lci)<0.01)] <- temp.df$y.lci

# upper bound
x.uci.1 <- seq(0, 2, 0.05)
y.uci.1 <- splinefun(x=c(0, 1, 1.5, 1.8, 2),
                     y=c(8.5, 7.5, 7.0, 6.9, 6.8))(x.uci.1)

x.uci.2 <- seq(2, 7, 0.05)
y.uci.2 <- splinefun(x=c(2, 3, 4, 6, 6.5, 7),
                     y=c(6.8, 7.4, 7.8, 8.2, 7.45, 5.6))(x.uci.2)

x.uci.3 <- seq(7, 8, 0.05)
y.uci.3 <- splinefun(x=c(7, 7.5, 8),
                     y=c(5.6, 4.6, 3.75))(x.uci.3)

x.uci.4 <- seq(8, 10, 0.05)
y.uci.4 <- splinefun(x=c(8, 8.5, 8.7, 9, 9.5, 10),
                     y=c(3.75, 3.8, 3.9, 4.2, 5.5, 7.2))(x.uci.4)

temp.df <- data.frame(x.uci=c(x.uci.1, x.uci.2, x.uci.3, x.uci.4), 
                      y.uci=c(y.uci.1, y.uci.2, y.uci.3, y.uci.4))
temp.df <- temp.df[!duplicated(temp.df$x.uci), ]

df$y.uci <- NULL
df$y.uci[which(abs(df$xx-temp.df$x.uci)<0.01)] <- temp.df$y.uci

# other curves
x.o.1 <- seq(0, 8, 0.05)
y.o.1 <- splinefun(x=seq(0, 8, 1),
                   y=c(0, 0, 0, 0, 0, 0, 0, 0, 0))(x.o.1)

x.o.2 <- seq(8, 10, 0.05)
y.o.2 <- splinefun(x=c(8, 8.5, 9, 9.5, 10),
                   y=c(0, 1, 0.75, 0.6, 0.5))(x.o.2)

temp.df <- data.frame(x.o=c(x.o.1, x.o.2), 
                      y.o=c(y.o.1, y.o.2))
temp.df <- temp.df[!duplicated(temp.df$x.o), ]

df$y.o <- NULL
df$y.o[which(abs(df$xx-temp.df$x.o)<0.01)] <- temp.df$y.o
df$y.o[which(df$y.o<0.01)] <- 0.01



p2 <- ggplot(df, aes(x = xx)) + 
  theme(
    panel.background = element_rect(fill = "white", color = "black"),  # 设置透明背景和图形边框
    panel.grid.major = element_blank(),  # 不显示网格线
    panel.grid.minor = element_blank(),  # 不显示网格线
    axis.title = element_blank(),  # 不显示坐标轴标签
    axis.text = element_blank(),  # 不显示坐标轴刻度
    axis.ticks = element_blank(), # 不显示坐标轴刻度线
    plot.margin = margin(t = 0.3, r = 0, b = 0, l = 0, unit = "inch")
  ) +
  scale_x_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) +  
  scale_y_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) + 
  geom_ribbon(aes(ymin = y.lci, ymax = y.uci), fill = "#d1e8ff") +
  geom_line(aes(y = y.true), color = "black") + 
  geom_line(aes(y = y.predict), color = "black", linetype = "dashed") + 
  # geom_line(aes(y = y.lci), color = "blue") +
  # geom_line(aes(y = y.uci), color = "blue") +
  # geom_ribbon(aes(ymin = y.lci, ymax = y.uci), fill = "#1E90FF", alpha = 0.2) +
  geom_line(aes(y = y.o), color = "orange") +
  geom_ribbon(aes(ymin = 0, ymax = y.o), fill = "#fff4e0")




## plot3
df <- data.frame(xx=seq(0, 10, 0.05))

# observation and objective function
y.true <- c(7.5, 6.8, 7.2, 7.2, 3.75, 6.0, 5.6, 3.9)
y.predict <- c(7.8, 6.8, 7.25, 7.65, 7.65, 7.05, 5.6, 3.75, 3.9, 4.5, 6.8)

df$y.true <- splinefun(x=c(seq(0, 10, 2), 7, 8.5), y.true)(df$xx)
df$y.predict <- splinefun(x=c(seq(0, 4, 2), 5, 6, 6.5, 7, 8, 8.5, 9, 10), y.predict)(df$xx)

# confidence interval
# lower bound
x.lci.1 <- seq(0, 2, 0.05)
y.lci.1 <- splinefun(x=c(0, 1, 1.5, 2),
                     y=c(6.4, 6.35, 6.45, 6.8))(x.lci.1)

x.lci.2 <- seq(2, 7, 0.05)
y.lci.2 <- splinefun(x=c(2, 2.2, 3, 4, 6, 7),
                     y=c(6.8, 6.5, 6.4, 6.5, 6.6, 5.6))(x.lci.2)

x.lci.3 <- seq(7, 8, 0.05)
y.lci.3 <- splinefun(x=c(7, 7.5, 8),
                     y=c(5.6, 4.35, 3.75))(x.lci.3)

x.lci.4 <- seq(8, 8.5, 0.05)
y.lci.4 <- splinefun(x=c(8, 8.25, 8.5),
                     y=c(3.75, 3.65, 3.9))(x.lci.4)

x.lci.5 <- seq(8.5, 10, 0.05)
y.lci.5 <- splinefun(x=c(8.5, 9, 9.5, 10),
                     y=c(3.9, 4.3, 4.75, 5.2))(x.lci.5)

temp.df <- data.frame(x.lci=c(x.lci.1, x.lci.2, x.lci.3, x.lci.4, x.lci.5), 
                      y.lci=c(y.lci.1, y.lci.2, y.lci.3, y.lci.4, y.lci.5))
temp.df <- temp.df[!duplicated(temp.df$x.lci), ]

df$y.lci <- NULL
df$y.lci[which(abs(df$xx-temp.df$x.lci)<0.01)] <- temp.df$y.lci

# upper bound
x.uci.1 <- seq(0, 2, 0.05)
y.uci.1 <- splinefun(x=c(0, 1, 1.5, 1.8, 2),
                     y=c(8.5, 7.5, 7.0, 6.9, 6.8))(x.uci.1)

x.uci.2 <- seq(2, 7, 0.05)
y.uci.2 <- splinefun(x=c(2, 3, 4, 6, 6.5, 7),
                     y=c(6.8, 7.4, 7.7, 8.1, 7.35, 5.6))(x.uci.2)

x.uci.3 <- seq(7, 8, 0.05)
y.uci.3 <- splinefun(x=c(7, 7.5, 8),
                     y=c(5.6, 4.6, 3.75))(x.uci.3)

x.uci.4 <- seq(8, 8.5, 0.05)
y.uci.4 <- splinefun(x=c(8, 8.25, 8.5),
                     y=c(3.75, 3.825, 3.9))(x.uci.4)

x.uci.5 <- seq(8.5, 10, 0.05)
y.uci.5 <- splinefun(x=c(8.5, 9, 9.5, 10),
                     y=c(3.9, 5.0, 5.8, 6.5))(x.uci.5)

temp.df <- data.frame(x.uci=c(x.uci.1, x.uci.2, x.uci.3, x.uci.4, x.uci.5), 
                      y.uci=c(y.uci.1, y.uci.2, y.uci.3, y.uci.4, y.uci.5))
temp.df <- temp.df[!duplicated(temp.df$x.uci), ]

df$y.uci <- NULL
df$y.uci[which(abs(df$xx-temp.df$x.uci)<0.01)] <- temp.df$y.uci

# other curves
x.o.1 <- seq(0, 8.2, 0.05)
y.o.1 <- splinefun(x=seq(0, 8, 1),
                   y=c(0, 0, 0, 0, 0, 0, 0, 0, 0))(x.o.1)

x.o.2 <- seq(8.2, 8.8, 0.05)
y.o.2 <- splinefun(x=c(8.2, 8.5, 8.8),
                   y=c(0, 1, 0))(x.o.2)

x.o.3 <- seq(8.8, 10, 0.05)
y.o.3 <- splinefun(x=c(8.8, 9, 9.5, 10),
                   y=c(0, 0, 0, 0))(x.o.3)

temp.df <- data.frame(x.o=c(x.o.1, x.o.2, x.o.3), 
                      y.o=c(y.o.1, y.o.2, y.o.3))
# temp.df <- temp.df[!duplicated(temp.df$x.o), ]
diff_x <- diff(temp.df$x.o)
remove_rows <- which(diff_x < 0.01)
temp.df <- temp.df[-(remove_rows + 1), ]


df$y.o <- NULL
df$y.o[which(abs(df$xx-temp.df$x.o)<0.01)] <- temp.df$y.o
df$y.o[which(df$y.o<0.01)] <- 0.01



p3 <- ggplot(df, aes(x = xx)) + 
  theme(
    panel.background = element_rect(fill = "white", color = "black"),  # 设置透明背景和图形边框
    panel.grid.major = element_blank(),  # 不显示网格线
    panel.grid.minor = element_blank(),  # 不显示网格线
    axis.title = element_blank(),  # 不显示坐标轴标签
    axis.text = element_blank(),  # 不显示坐标轴刻度
    axis.ticks = element_blank(), # 不显示坐标轴刻度线
    plot.margin = margin(t = 0.3, r = 0, b = 0, l = 0, unit = "inch")
  ) +
  scale_x_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) +  
  scale_y_continuous(expand = c(0.001, 0.001), limits = c(0, 10)) + 
  geom_ribbon(aes(ymin = y.lci, ymax = y.uci), fill = "#d1e8ff") +
  geom_line(aes(y = y.true), color = "black") + 
  geom_line(aes(y = y.predict), color = "black", linetype = "dashed") + 
  # geom_line(aes(y = y.lci), color = "blue") +
  # geom_line(aes(y = y.uci), color = "blue") +
  # geom_ribbon(aes(ymin = y.lci, ymax = y.uci), fill = "#1E90FF", alpha = 0.2) +
  geom_line(aes(y = y.o), color = "orange") +
  geom_ribbon(aes(ymin = 0, ymax = y.o), fill = "#fff4e0")













plot_combined <- plot_grid(p1, p2, p3, ncol = 1)
ggsave("C:/Users/LY/Desktop/figure2.svg", plot_combined, device = "svg", width = 5, height = 6, units = "in")

