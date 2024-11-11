# Problem:
Food enthusiasts and home cooks struggle to find similar dishes in indian Cuisne that match their taste preferences and dietary restrictions across different cuisines, leading to limited culinary exploration and repetitive meal choices.
# Target users: 
Primarily food enthusiasts, Restaurant owners, health-conscious individuals, and home cooks who want to explore similar dishes while maintaining their dietary preferences (vegetarian/non-vegetarian).
# Solution Highlight: 
FlavorMatch uses AWS Bedrock's Titan model to generate high-quality food images and Claude-3 for intelligent dish recommendations, helping users visualize and discover similar dishes while respecting their dietary preferences through vector similarity search.


# 🍽️ FlavorMatch

FlavorMatch is an AI-powered food recommendation system that helps users discover similar dishes based on ingredients, cuisine types, and dietary preferences. Using advanced natural language processing and image generation capabilities, it provides personalized food suggestions along with visually appealing representations of recommended dishes.

## 🌟 Features

- **Intelligent Food Matching**: Utilizes sentence transformers and vector similarity search to find similar dishes
- **Dietary Preference Support**: Handles both vegetarian and non-vegetarian preferences
- **AI-Generated Food Images**: Creates high-quality food images using AWS Bedrock's Titan model
- **Smart Description Generation**: Provides detailed dish descriptions using Claude-3 AI
- **Vector Search**: Efficient similarity search using MongoDB Atlas vector search capabilities
- 
## 🚀 Architecture:
<img width="1462" alt="image" src="https://github.com/user-attachments/assets/f86dd8f2-c21f-4ffe-aa28-669047b19529">

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **AI/ML**: 
  - AWS Bedrock (Claude-3 & Titan)
  - Sentence Transformers
- **Database**: MongoDB Atlas with Vector Search
- **Cloud Storage**: AWS S3
- **Image Processing**: Pillow, OpenCV

## ⚙️ Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- MongoDB Atlas account
- Required Python packages (see requirements.txt)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/FlavorMatch.git
   cd FlavorMatch
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up MongoDB**
   - Create a MongoDB Atlas cluster
   - Update the MongoDB connection string in the code
   - Create the required indexes for vector search on ingredinets 
   - 5. **Configure AWS credentials**
   - Extact "recipes_with_embeddings" in this repo and place it in mongodb
   - Update `config/config.ini` with your AWS credentials:
   ```in
   
   [aws]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = us-west-2
   [mongodb]
   user=XXX
   password=XXX
   ```


6. **Create required directories**
   ```bash
   mkdir -p static/generated_images
   ```

## 🎯 Usage

1. **Start the application**
   ```bash
   python run.py (Runs of 4440)
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://localhost:4440`
   - Enter a food item in the search bar
   - View similar food recommendations with AI-generated images

## 📝 Configuration

### MongoDB Setup
- Ensure your MongoDB Atlas cluster has vector search enabled
- Create required indexes:
```javascript
db.recipes_embeddings.createIndex(
  { ingredients_embeddings: "vector", Diet: 1 },
  {
    name: "diet_vector_index",
    vectors: {
      numDimensions: 384,
      similarity: "cosine"
    }
  }
)
```

### AWS Bedrock Models
- Ensure your AWS account has access to:
  - Claude-3 Sonnet model for text generation
  - Titan Image Generator for food images

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request



## 🙏 Acknowledgments

- AWS Bedrock team for AI capabilities
- MongoDB Atlas for vector search functionality
- Sentence Transformers library
- Flask community

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact aditya.kommu@gmail.com

