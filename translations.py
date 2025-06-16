"""
Internationalization and localization support for the content management system
"""

# Korean translations for the website interface
TRANSLATIONS = {
    'ko': {
        # Navigation
        'content': '콘텐츠',
        'gallery': '갤러리',
        'file_manager': '파일 관리자',
        'trending': '인기',
        'analytics': '분석',
        'trading_view': '트레이딩 뷰',
        'ai_insights': 'AI 인사이트',
        'cf_analytics': 'CF 분석',
        'database_admin': '데이터베이스 관리',
        'for_you': '추천',
        'advanced': '고급',
        'cf_tutorial': 'CF 튜토리얼',
        'cf_visualization': 'CF 시각화',
        'create': '만들기',
        'my_dashboard': '내 대시보드',
        'logout': '로그아웃',
        
        # Content Management
        'title': '제목',
        'content_text': '내용',
        'category': '카테고리',
        'status': '상태',
        'author': '작성자',
        'tags': '태그',
        'image': '이미지',
        'files': '파일',
        'created_at': '생성일',
        'updated_at': '수정일',
        
        # Status
        'draft': '초안',
        'published': '게시됨',
        'archived': '보관됨',
        
        # Categories
        'blog_post': '블로그 포스트',
        'news_article': '뉴스 기사',
        'product_description': '제품 설명',
        'documentation': '문서',
        'tutorial': '튜토리얼',
        'case_study': '사례 연구',
        'whitepaper': '백서',
        'press_release': '보도 자료',
        'user_guide': '사용자 가이드',
        'technical_spec': '기술 사양',
        
        # Actions
        'edit': '편집',
        'delete': '삭제',
        'save': '저장',
        'cancel': '취소',
        'submit': '제출',
        'create_content': '콘텐츠 만들기',
        'update_content': '콘텐츠 업데이트',
        'view_content': '콘텐츠 보기',
        'upload': '업로드',
        'download': '다운로드',
        
        # Messages
        'content_created': '콘텐츠가 성공적으로 생성되었습니다',
        'content_updated': '콘텐츠가 성공적으로 업데이트되었습니다',
        'content_deleted': '콘텐츠가 성공적으로 삭제되었습니다',
        'file_uploaded': '파일이 성공적으로 업로드되었습니다',
        'error_occurred': '오류가 발생했습니다',
        'permission_denied': '권한이 거부되었습니다',
        'content_not_found': '콘텐츠를 찾을 수 없습니다',
        
        # Forms
        'required_field': '필수 입력란',
        'optional': '선택사항',
        'characters': '문자',
        'words': '단어',
        'days_old': '일 전',
        'select_option': '옵션 선택',
        
        # Dashboard
        'welcome': '환영합니다',
        'total_content': '총 콘텐츠',
        'published_content': '게시된 콘텐츠',
        'draft_content': '초안 콘텐츠',
        'recent_activity': '최근 활동',
        'recommendations': '추천',
        'performance': '성능',
        'statistics': '통계',
        
        # File Management
        'file_type': '파일 유형',
        'file_size': '파일 크기',
        'upload_date': '업로드 날짜',
        'owner': '소유자',
        'documents': '문서',
        'images': '이미지',
        'videos': '비디오',
        'audio': '오디오',
        'archives': '압축 파일',
        
        # Search and Filter
        'search': '검색',
        'filter': '필터',
        'all_categories': '모든 카테고리',
        'all_status': '모든 상태',
        'sort_by': '정렬 기준',
        'newest_first': '최신순',
        'oldest_first': '오래된순',
        'title_az': '제목 A-Z',
        'title_za': '제목 Z-A',
        
        # Pagination
        'previous': '이전',
        'next': '다음',
        'page': '페이지',
        'of': '/',
        'showing': '표시 중',
        'results': '결과',
        
        # Time
        'just_now': '방금 전',
        'minutes_ago': '분 전',
        'hours_ago': '시간 전',
        'days_ago': '일 전',
        'weeks_ago': '주 전',
        'months_ago': '달 전',
        
        # Analytics
        'views': '조회수',
        'interactions': '상호작용',
        'users': '사용자',
        'engagement': '참여도',
        'growth': '성장률',
        'trends': '트렌드',
        'insights': '인사이트',
        'reports': '보고서',
        
        # AI Features
        'ai_analysis': 'AI 분석',
        'relevance_score': '관련성 점수',
        'quality_score': '품질 점수',
        'engagement_score': '참여도 점수',
        'recommendations_for_you': '맞춤 추천',
        'ai_suggestions': 'AI 제안',
        
        # User Interface
        'loading': '로딩 중...',
        'no_data': '데이터가 없습니다',
        'error': '오류',
        'success': '성공',
        'warning': '경고',
        'info': '정보',
        'confirm': '확인',
        'yes': '예',
        'no': '아니오',
        'close': '닫기',
        'refresh': '새로고침',
        'settings': '설정',
        'help': '도움말',
        'about': '정보',
        'contact': '연락처',
        'privacy': '개인정보보호',
        'terms': '이용약관',
        
        # Language
        'language': '언어',
        'english': 'English',
        'korean': '한국어',
        'change_language': '언어 변경',
        'language_changed': '언어가 변경되었습니다',
    }
}

# Default language
DEFAULT_LANGUAGE = 'en'

def get_translation(key, language='en'):
    """
    Get translation for a given key and language
    
    Args:
        key: Translation key
        language: Language code (default: 'en')
        
    Returns:
        Translated string or original key if not found
    """
    if language in TRANSLATIONS and key in TRANSLATIONS[language]:
        return TRANSLATIONS[language][key]
    return key

def get_available_languages():
    """
    Get list of available languages
    
    Returns:
        Dictionary of language codes and names
    """
    return {
        'en': 'English',
        'ko': '한국어'
    }

def translate_dict(data, language='en'):
    """
    Translate a dictionary of values
    
    Args:
        data: Dictionary to translate
        language: Target language
        
    Returns:
        Dictionary with translated values
    """
    if not isinstance(data, dict):
        return data
        
    translated = {}
    for key, value in data.items():
        if isinstance(value, str):
            translated[key] = get_translation(value, language)
        elif isinstance(value, dict):
            translated[key] = translate_dict(value, language)
        elif isinstance(value, list):
            translated[key] = [get_translation(item, language) if isinstance(item, str) else item for item in value]
        else:
            translated[key] = value
    
    return translated