# Duke ChatBot
**Duke AIPI 540 Individual Project**

## Duke ChatBot (Streamlit App):
A streamlit-based web application which allows you to ask any Duke related question and get answers from the Duke ChatBot.
>![screenshot.png](assets/screenshot.png)

## Running the Code

**1. Clone the repository**
```bash
git clone https://github.com/guptashrey/Duke-ChatBot
```

**2. Switch to the `st` branch**
```bash
git checkout st
```

**3. Create a conda environment and activate it:** 
```bash
conda create --name streamlit python=3.8
conda activate streamlit
```

**4. Install requirements:** 
```bash
pip install -r requirements.txt
```

**5. Change directory to the scripts folder:** 
```bash
cd scripts
```

**6. Run the application**
```bash
streamlit run streamlit_app.py
```