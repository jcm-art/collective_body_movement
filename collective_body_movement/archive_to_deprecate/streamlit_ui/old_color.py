
class MetricsColorScaleManager:

    def __init__(self) -> None:
        
        self.colorscale_data = np.arange(256).repeat(256).reshape(256,256).T/256
        
        self.color_df = pd.DataFrame()
        color_x_data = np.arange(0,1,1/1024)
        color_y_data = np.zeros_like(color_x_data)+1
        self.color_df["x"] = color_x_data
        self.color_df["y"] = color_y_data

        self.color_manipulator = ColorManipulator()
        #fig = px.imshow(colorscale_data, color_continuous_scale=[first_color, second_color])
        #fig.update_xaxes(visible=False)
        #fig.update_yaxes(visible=False)

        #st.write(fig)

    def write(self):
        first_color = st.color_picker('Pick the first Color', '#8C00F9')
        second_color = st.color_picker('Pick the second Color', '#FFCE00')

        color_scale_fig = px.scatter(
            self.color_df, x="x", y="y", color="x",
            color_continuous_scale=[first_color, second_color])
        
        st.plotly_chart(color_scale_fig)



    def update_color_manager(self, dataset_id, metric_data, user_metric_selection):

        pass
        '''_self.dataset_id = dataset_id
        _self.metric_data = metric_data
        _self.user_metric_selection = user_metric_selection

        _self.dataset_metric = _self.metric_data[_self.metric_data["data_collect_name"] == dataset_id][user_metric_selection].values[0]
        _self.metric_array = _self.metric_data[_self.user_metric_selection].to_numpy()'''

        metric_color = self.color_manipulator.interpolate_colors(
            self.metric_array.min(), 
            self.metric_array.max(), first_color, second_color, 
            self.dataset_metric
        )

        html_string = f"<p style=\"color:{metric_color}\">This is the user's metric color.</p>"
        st.markdown(html_string, unsafe_allow_html=True)

        self.metrics_fig.add_trace(
            go.Histogram(x=self.metric_data[self.user_metric_selection]),
            row=1, col=1)
        self.metrics_fig.add_trace(
            go.Scatter(x=[self.dataset_metric], y=[0], mode="markers", marker=dict(color=metric_color, size=10)),
            row=1, col=1
        )
        # TODO - add custom color heatmap Custom Heatmap Color scale with Graph Objects https://plotly.com/python/colorscales/

        color_df = self.metric_data
        color_df["fake_y"]=0

        color_scale_fig = px.scatter(color_df, x=self.user_metric_selection, y="fake_y", color=self.user_metric_selection,color_continuous_scale=[first_color, second_color])
        st.plotly_chart(color_scale_fig)
        max_metric = self.metric_array.max()
        min_metric = self.metric_array.min()
        st.plotly_chart(self.metrics_fig)
