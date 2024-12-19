def get_html_template():
    """
    Returns HTML template following TRMNL design system
    """
    return '''
    <div class="view view--full">
        <div class="layout layout--col gap--large">
            <!-- Ship Info -->
            <div class="item">
                <div class="meta">
                    <span class="index">1</span>
                </div>
                <div class="content">
                    <span class="title">{{ship_name}}</span>
                    <span class="description">MMSI: {{mmsi}}</span>
                </div>
            </div>

            <!-- Position Data -->
            <div class="item bg-white">
                <div class="content">
                    <span class="value value--large value--tnums">{{lat}}, {{lon}}</span>
                    <span class="label">Position</span>
                </div>
            </div>

            <!-- Speed and Course -->
            <div class="layout layout--row gap">
                <div class="item bg-white">
                    <div class="content">
                        <span class="value value--large value--tnums">{{speed}}</span>
                        <span class="label">Speed (knots)</span>
                    </div>
                </div>
                <div class="item bg-white">
                    <div class="content">
                        <span class="value value--large value--tnums">{{course}}°</span>
                        <span class="label">Course</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="title_bar">
            <img class="image" src="ship_icon.png" />
            <span class="title">Ship Tracker</span>
            <span class="instance">Last Update: {{timestamp}}</span>
        </div>
    </div>
    '''