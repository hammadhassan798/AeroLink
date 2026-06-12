import heapq
from datetime import datetime

class FlightMinHeap:
    def __init__(self):
        self.heap = []

    def _time_diff_minutes(self, departure_time):
        now = datetime.now()
        diff = departure_time - now
        return max(int(diff.total_seconds() // 60), 0)

    def push(self, flight):
        priority = self._time_diff_minutes(flight["departure_time"])
        heapq.heappush(
            self.heap,
            (priority, flight["flight_no"], flight)
        )

    def get_all_sorted(self):
        sorted_items = heapq.nsmallest(len(self.heap), self.heap)
        return [item[2] for item in sorted_items]