SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Games](
	[Id] [varchar](50) NOT NULL,
	[GameStatus] [int] NULL,
	[GameType] [varchar](50) NOT NULL,
	[Params] [varchar](1024) NOT NULL,
	[Created] [datetime2](7) NOT NULL,
	[UserID] [varchar](30) NULL,
	[Completed] [datetime2](7) NULL,
	[Score] [int] NOT NULL
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
ALTER TABLE [dbo].[Games] ADD PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Games] ADD  DEFAULT ((0)) FOR [Score]
GO
ALTER TABLE [dbo].[Games]  WITH CHECK ADD FOREIGN KEY([UserID])
REFERENCES [dbo].[Users] ([UserID])
GO
