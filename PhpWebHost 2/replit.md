# Dynamic Content Manager

## Overview

This is a Flask-based web application for managing dynamic content such as blog posts, articles, and documentation. The application provides a user-friendly interface for creating, editing, viewing, and organizing content with features like categorization, status management, and search functionality.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5 with Replit dark theme
- **JavaScript**: Vanilla JavaScript for interactive features
- **Icons**: Font Awesome for consistent iconography
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Form Handling**: Flask-WTF with WTForms for form validation
- **Session Management**: Flask sessions with configurable secret key
- **Data Storage**: PostgreSQL database with Content model
- **WSGI Server**: Gunicorn for production deployment

### Application Structure
```
/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── forms.py            # WTForms form definitions
├── templates/          # Jinja2 HTML templates
├── static/js/          # Client-side JavaScript
└── pyproject.toml      # Python dependencies
```

## Key Components

### Content Management System
- **Content Model**: Stores title, content, category, status, author, tags, images, and timestamps
- **Categories**: Predefined content types (Blog Post, News Article, Product Description, etc.)
- **Status System**: Draft, Published, Archived workflow
- **Tagging System**: Comma-separated tags for content organization
- **Image Management**: Upload, display, and manage images with content
- **Rich Text Editor**: Quill.js-powered editor with comprehensive formatting toolbar and auto-save functionality

### Image Management System
- **File Upload**: Support for PNG, JPG, JPEG, GIF, WEBP, and SVG formats
- **Image Storage**: Local file system storage with unique filename generation
- **Image Gallery**: Dedicated gallery view for browsing all uploaded images
- **Image Integration**: Images displayed in content cards, detailed views, and gallery
- **Image Preview**: Real-time preview during upload and editing

### Recommendation System
- **Content Similarity**: Analyzes categories, tags, keywords, and authors to find related content
- **Collaborative Filtering (CF)**: User behavior analysis with cosine similarity calculations
- **Hybrid Recommendations**: Combines content-based (60%) and collaborative filtering (40%) approaches
- **User Interaction Tracking**: Records views, edits, and other actions with weighted scoring
- **Trending Content**: Identifies popular content based on tag frequency and recency
- **Category Suggestions**: Displays related articles from the same category
- **CF Analytics Dashboard**: Real-time insights into user behavior patterns and recommendation performance

### Form Validation
- **ContentForm**: For creating new content with comprehensive validation
- **EditContentForm**: For updating existing content
- **Validation Rules**: Length constraints, required fields, and data sanitization

### Rich Text Editor System
- **Quill.js Integration**: Professional-grade rich text editor with comprehensive formatting options
- **Formatting Features**: Headers (H1-H6), bold, italic, underline, strikethrough, text colors, background colors
- **Lists and Alignment**: Ordered lists, bullet lists, text alignment options, indentation controls
- **Media Support**: Link insertion, image embedding, video embedding capabilities
- **Advanced Features**: Code blocks, blockquotes, subscript, superscript formatting
- **Auto-Save**: Content automatically saves every 30 seconds with visual indicators
- **Real-Time Preview**: Live preview functionality during content creation and editing
- **Seamless Integration**: Works consistently across both create and edit content pages

### Authentication System
- **Replit Auth Integration**: Secure OpenID Connect authentication through Replit's OAuth service
- **User Management**: User profiles with email, name, and profile image support
- **Session Management**: Persistent login sessions with automatic token refresh
- **Access Control**: Protected routes requiring authentication for content creation and editing
- **Landing Page**: Welcome page for unauthenticated users with feature overview
- **User Dashboard**: Personalized content dashboard for authenticated users

### User Interface
- **Landing Page**: Feature-rich welcome page for new users with login prompts
- **Dashboard**: Overview of all content with filtering and search (authenticated users)
- **Content Creation**: Rich text editor with advanced formatting and real-time preview (requires login)
- **Content Editing**: Rich text editor preserving existing formatting with auto-save (requires login)
- **Content Viewing**: Clean, readable content display with proper HTML rendering
- **User Profile**: Navigation dropdown showing user information and logout option

## Data Flow

1. **Content Creation**:
   - User fills out ContentForm
   - Form validation on client and server side
   - Data stored in in-memory content_store with auto-incrementing ID
   - Timestamps automatically added

2. **Content Retrieval**:
   - Homepage displays filtered content based on category, status, and search terms
   - Individual content accessed via unique ID
   - Real-time filtering without page reload

3. **Content Updates**:
   - Existing content loaded into EditContentForm
   - Changes validated and updated in storage
   - Updated timestamp automatically set

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and middleware
- **Gunicorn**: Production WSGI server
- **Email-validator**: Email validation for forms
- **psycopg2-binary**: PostgreSQL adapter (prepared for future database integration)

### Frontend Dependencies
- **Bootstrap 5**: UI framework with Replit theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No additional frontend frameworks

## Deployment Strategy

### Development Environment
- **Server**: Flask development server with auto-reload
- **Host**: 0.0.0.0:5000 for Replit compatibility
- **Debug Mode**: Enabled for development

### Production Environment
- **Server**: Gunicorn with auto-scaling deployment target
- **Configuration**: Proxy fix for proper header handling
- **Environment Variables**: Session secret from environment
- **Port**: 5000 with bind to all interfaces

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **System Packages**: OpenSSL and PostgreSQL prepared for future use
- **Workflow**: Parallel execution with automatic port detection

## Changelog

- June 14, 2025. Initial setup with basic content management
- June 14, 2025. Added comprehensive image management system with upload, gallery, and integration features
- June 14, 2025. Migrated from in-memory storage to PostgreSQL database with SQLAlchemy ORM
- June 15, 2025. Implemented intelligent recommendation system with content similarity analysis, trending content detection, and personalized suggestions
- June 15, 2025. Added Collaborative Filtering (CF) system with user interaction tracking, hybrid recommendations, and real-time analytics dashboard
- June 15, 2025. Enhanced database integration with PostgreSQL optimization, full-text search, performance indexing, admin dashboard, and automated backup systems
- June 15, 2025. Implemented rich text editor using Quill.js with comprehensive formatting toolbar, auto-save functionality, and seamless integration for both content creation and editing
- June 15, 2025. Removed authentication system and restored application to work without user login requirements - all content management features are now available to all users
- June 15, 2025. Enhanced visual design with custom CSS styling including: modern light theme with animated background particles, improved typography with Inter font, modern card designs with glass-morphism effects, enhanced buttons with gradients and hover animations, improved form styling, and responsive design improvements

## User Preferences

Preferred communication style: Simple, everyday language.

## Notes for Future Development

### Enhanced Database Integration
- **PostgreSQL with SQLAlchemy ORM**: Full persistent storage with optimized schema design
- **Database Indexing**: Performance-optimized indexes for queries, search, and analytics
- **Full-Text Search**: PostgreSQL TSVECTOR with automatic trigger updates and GIN indexing
- **Data Constraints**: Database-level validation with check constraints and foreign keys
- **Database Administration**: Comprehensive admin dashboard with health monitoring and optimization tools
- **Backup and Recovery**: Automated backup creation with pg_dump integration
- **Performance Monitoring**: Real-time database statistics and query performance metrics
- **Data Cleanup**: Automated cleanup routines for maintaining optimal performance

### Authentication System
The application includes session management infrastructure and can be extended with user authentication, role-based access control, and multi-user content management.

### API Development
The current architecture can be extended to include REST API endpoints for headless content management or mobile application integration.

### Content Features
Future enhancements could include content versioning, rich text editing, file uploads, content scheduling, and advanced search with full-text indexing.