import arrow
import re

class DateParser:
    def __init__(self):
        self.today = arrow.now('Asia/Seoul')
    
    def parse_korean_date(self, text):
        """한국어 날짜 표현 파싱"""
        text = text.lower()
        
        # 상대적 날짜
        if '오늘' in text:
            return self.today.format('YYYY-MM-DD')
        elif '내일' in text:
            return self.today.shift(days=1).format('YYYY-MM-DD')
        elif '모레' in text:
            return self.today.shift(days=2).format('YYYY-MM-DD')
        elif '어제' in text:
            return self.today.shift(days=-1).format('YYYY-MM-DD')
        elif '그제' in text:
            return self.today.shift(days=-2).format('YYYY-MM-DD')
        
        # 요일 기반
        weekdays = {'월요일': 0, '화요일': 1, '수요일': 2, '목요일': 3, 
                   '금요일': 4, '토요일': 5, '일요일': 6}
        
        for day_name, day_num in weekdays.items():
            if day_name in text:
                days_ahead = day_num - self.today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return self.today.shift(days=days_ahead).format('YYYY-MM-DD')
        
        # 숫자 패턴 (YYYY-MM-DD, MM/DD 등)
        patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})/(\d{1,2})',
            r'(\d{1,2})월\s*(\d{1,2})일'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:  # YYYY-MM-DD
                    year, month, day = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif len(match.groups()) == 2:  # MM/DD or MM월 DD일
                    month, day = match.groups()
                    year = self.today.year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # 기본값: 오늘
        return self.today.format('YYYY-MM-DD')
    
    def is_valid_date(self, date_str):
        """날짜 유효성 검사"""
        try:
            arrow.get(date_str, 'YYYY-MM-DD')
            return True
        except:
            return False
