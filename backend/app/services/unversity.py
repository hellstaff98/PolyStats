from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException, status

class UniversityService:
    BASE_URL = "https://ruz.spbstu.ru/api/v1/ruz"

    async def get_group_id_by_number(self, group_name: str) -> int:
        """
        Получает ID группы по её названию (например, '5130904/30105').
        """
        url = f"{self.BASE_URL}/search/groups"
        params = {"q": group_name}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
            except httpx.HTTPError as e:
                # Если API университета недоступно
                print(f"University API Error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Сервис расписания университета временно недоступен"
                )

        data = response.json()
        groups = data.get("groups", [])

        if not groups:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Группа '{group_name}' не найдена"
            )

        target_group = groups[0]

        return target_group["id"]

    def _get_mid_semester_date(self) -> str:
        """Определяет дату в середине семестра для получения полного списка предметов."""
        now = datetime.now()
        # Если сейчас осень/начало зимы (до конца января)
        if now.month >= 9 or now.month == 1:
            year = now.year if now.month >= 9 else now.year - 1
            return f"{year}-11-10"
        # Если весна/лето
        else:
            return f"{now.year}-04-10"

    async def get_subjects_list(self, group_id: int) -> list[str]:
        """
        Получает уникальный список предметов за 2 недели в середине семестра.
        """
        target_date_str = self._get_mid_semester_date()
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

        dates_to_check = [
            target_date_str,
            (target_date + timedelta(days=7)).strftime("%Y-%m-%d")
        ]

        unique_subjects = set()

        async with httpx.AsyncClient() as client:
            for date_param in dates_to_check:
                url = f"{self.BASE_URL}/scheduler/{group_id}"
                params = {"date": date_param}

                try:
                    response = await client.get(url, params=params, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()

                    for day in data.get("days", []):
                        for lesson in day.get("lessons", []):
                            subject_name = lesson.get("subject")
                            if subject_name:
                                unique_subjects.add(subject_name.strip())

                except Exception as e:
                    print(f"Error fetching schedule for {date_param}: {e}")
                    continue

        return list(unique_subjects)

uni_service = UniversityService()

