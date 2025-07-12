# **TuneGrab - Learning Project**

A **learning-focused** Python application built to understand GUI development, API integration, and audio processing. This project explores how to create desktop applications with Python while learning about Spotify API, audio conversion, and modern GUI frameworks.

---

## 🎯 **Learning Objectives**

This project was built to understand:

### **Python Development**
- Object-oriented programming concepts
- GUI development with CustomTkinter
- File system operations and management
- Error handling and user feedback
- Cross-platform compatibility

### **API Integration**
- RESTful API concepts with Spotify API
- Authentication and credential management
- JSON data handling and parsing
- Rate limiting and error handling
- Environment variable management

### **Audio Processing**
- Understanding audio formats and conversion
- FFmpeg integration for audio processing
- Download management and progress tracking
- File organization and naming conventions

---

## 🔧 **What I Learned**

### **Desktop Application Development**
- How to create modern GUI applications with Python
- Event-driven programming patterns
- User interface design principles
- Cross-platform deployment considerations

### **API Understanding**
- Spotify Web API integration
- OAuth authentication flows
- API response handling and error management
- Rate limiting and best practices

### **Audio Technology**
- MP3 format and audio conversion
- YouTube-DL integration for content downloading
- FFmpeg command-line integration
- Audio metadata handling

### **Development Skills**
- Python package management
- Environment variable security
- Error handling and user feedback
- Code organization and maintainability

---

## 🚀 **Live Demo**

![image](https://github.com/user-attachments/assets/b5381964-3d20-4f36-a9a9-c2eede32b6cd)

---

## 🛠️ **Tech Stack & Learning Focus**

| Technology | What I Learned |
|------------|----------------|
| **Python 3.8+** | OOP, GUI development, file operations |
| **CustomTkinter** | Modern GUI frameworks, event handling |
| **Spotify API** | RESTful APIs, authentication, JSON handling |
| **yt-dlp** | Content downloading, audio extraction |
| **FFmpeg** | Audio processing, format conversion |

---

## 📂 **Project Structure**

```
📁 TuneGrab/
├── app.py              # Main application and GUI logic
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not tracked)
├── songs/             # Downloaded audio files
└── README.md          # This documentation
```

---

## 🧠 **Key Learning Concepts**

### **Python GUI Development**
- CustomTkinter widget system
- Event-driven programming patterns
- Threading for background operations
- Progress tracking and user feedback

### **API Integration Patterns**
- Spotify Web API authentication
- Playlist and track data retrieval
- Error handling and retry logic
- Rate limiting considerations

### **Audio Processing**
- FFmpeg command-line integration
- Audio format conversion (MP3)
- Download progress monitoring
- File system organization

### **Security Best Practices**
- Environment variable usage
- API credential management
- Input validation and sanitization
- Error message handling

---

## 📦 **Installation & Setup**

### **Prerequisites**
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **FFmpeg**: Required for audio processing. [Download FFmpeg](https://ffmpeg.org/download.html)
- **Spotify Developer Account**: For API credentials

### **Setup Steps**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mosesfdo/TuneGrab.git
   cd TuneGrab
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Spotify API**:
   - Create a [Spotify Developer Account](https://developer.spotify.com)
   - Get your `client_id` and `client_secret`
   - Add to environment variables or `.env` file:
     ```bash
     export SPOTIFY_CLIENT_ID="your_client_id"
     export SPOTIFY_CLIENT_SECRET="your_client_secret"
     ```

4. **Install FFmpeg**:
   - **Windows**: Add to PATH or place in `C:\ffmpeg\bin`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

5. **Run the Application**:
   ```bash
   python app.py
   ```

---

## 🔮 **Future Learning Goals**

- [ ] Add support for other music platforms
- [ ] Implement database for download history
- [ ] Add audio quality selection options
- [ ] Create installer packages for distribution
- [ ] Add playlist management features
- [ ] Explore async/await patterns for better performance

---

## 📚 **Resources That Helped**

- Spotify Web API documentation
- CustomTkinter tutorials and examples
- Python threading and GUI development guides
- FFmpeg command-line reference
- Audio format and conversion guides

---

## 🧑‍💻 **About This Project**

This was created as a **learning exercise** to understand:
- How desktop applications are built with Python
- How to integrate external APIs into applications
- How audio processing and conversion works
- Best practices for GUI development and user experience

The goal was to build a functional application while learning the fundamentals of Python development, API integration, and audio technology.

---

## 📄 **License**

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♂️ **About Me**

**Moses**  
Student & Aspiring AI Engineer  
[GitHub](https://github.com/mosesfdo) • [LinkedIn](https://linkedin.com/in/mosesfdo)

*This project represents my journey into Python development, API integration, and desktop application creation. I built this to understand how modern applications work with external services and handle complex operations like audio processing.*

---

## ⚠️ **Disclaimer**

This project is for **educational purposes only**. Downloading music may violate Terms of Service. Ensure compliance with applicable laws and platform terms.

---

> **Note**: This app demonstrates API integration and audio processing concepts. Use responsibly and in accordance with platform terms of service.
