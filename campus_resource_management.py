from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class Resource:
    resource_id: str
    name: str
    category: str
    total_units: int
    available_units: int


class CampusResourceManager:
    def __init__(self) -> None:
        self.resources: Dict[str, Resource] = {}
        self.loans: Dict[Tuple[str, str], int] = {}
        self.borrow_log: List[dict] = []

    def add_resource(self, resource_id: str, name: str, category: str, total_units: int) -> bool:
        resource_id = resource_id.strip()
        if not resource_id or resource_id in self.resources:
            return False
        if total_units <= 0:
            return False
        self.resources[resource_id] = Resource(
            resource_id=resource_id,
            name=name.strip(),
            category=category.strip(),
            total_units=total_units,
            available_units=total_units,
        )
        return True

    def list_resources(self) -> List[Resource]:
        return list(self.resources.values())

    def borrow_resource(self, fellow_id: str, resource_id: str, quantity: int) -> bool:
        fellow_id = fellow_id.strip()
        resource_id = resource_id.strip()
        if not fellow_id or not resource_id or quantity <= 0:
            return False
        resource = self.resources.get(resource_id)
        if resource is None or quantity > resource.available_units:
            return False

        resource.available_units -= quantity
        key = (fellow_id, resource_id)
        self.loans[key] = self.loans.get(key, 0) + quantity
        self.borrow_log.append(
            {
                "fellow_id": fellow_id,
                "resource_id": resource_id,
                "quantity": quantity,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        )
        return True

    def return_resource(self, fellow_id: str, resource_id: str, quantity: int) -> bool:
        fellow_id = fellow_id.strip()
        resource_id = resource_id.strip()
        if not fellow_id or not resource_id or quantity <= 0:
            return False

        key = (fellow_id, resource_id)
        current_loan = self.loans.get(key, 0)
        resource = self.resources.get(resource_id)
        if resource is None or quantity > current_loan:
            return False

        if quantity == current_loan:
            del self.loans[key]
        else:
            self.loans[key] = current_loan - quantity
        resource.available_units += quantity
        return True

    def search_by_name(self, name_query: str) -> List[Resource]:
        query = name_query.strip().lower()
        return [resource for resource in self.resources.values() if query in resource.name.lower()]

    def filter_by_category(self, category: str) -> List[Resource]:
        category_lower = category.strip().lower()
        return [resource for resource in self.resources.values() if resource.category.lower() == category_lower]

    def generate_report(self) -> dict:
        total_units = sum(resource.total_units for resource in self.resources.values())
        available_units = sum(resource.available_units for resource in self.resources.values())
        units_borrowed = total_units - available_units

        low_stock = [resource for resource in self.resources.values() if resource.available_units < 3]

        borrowed_per_resource: Dict[str, int] = {
            resource_id: 0 for resource_id in self.resources
        }
        for (_, resource_id), quantity in self.loans.items():
            borrowed_per_resource[resource_id] = borrowed_per_resource.get(resource_id, 0) + quantity

        leaders: List[Resource] = []
        if borrowed_per_resource:
            max_borrowed = max(borrowed_per_resource.values())
            if max_borrowed > 0:
                leaders = [
                    self.resources[resource_id]
                    for resource_id, qty in borrowed_per_resource.items()
                    if qty == max_borrowed
                ]

        return {
            "total_units": total_units,
            "available_units": available_units,
            "units_borrowed": units_borrowed,
            "low_stock_resources": low_stock,
            "most_borrowed_resources": leaders,
            "borrowed_per_resource": borrowed_per_resource,
        }


def _prompt_positive_int(prompt: str) -> int | None:
    raw_value = input(prompt).strip()
    if not raw_value.isdigit() or int(raw_value) <= 0:
        print("Quantity must be a positive integer.")
        return None
    return int(raw_value)


def _print_resources(resources: List[Resource]) -> None:
    if not resources:
        print("No resources found.")
        return
    print("ID | Name | Category | Total | Available")
    for resource in resources:
        print(
            f"{resource.resource_id} | {resource.name} | {resource.category} | "
            f"{resource.total_units} | {resource.available_units}"
        )


def run_cli() -> None:
    manager = CampusResourceManager()

    while True:
        print("\nCampus Resource Management System")
        print("1. Add resource")
        print("2. List resources")
        print("3. Borrow resource")
        print("4. Return resource")
        print("5. Search resource by name")
        print("6. Filter resources by category")
        print("7. Reports")
        print("8. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            resource_id = input("Resource ID: ").strip()
            name = input("Name: ").strip()
            category = input("Category: ").strip()
            total_units = _prompt_positive_int("Total units: ")
            if total_units is None:
                continue
            if not name or not category:
                print("Name and category are required.")
                continue
            if manager.add_resource(resource_id, name, category, total_units):
                print("Resource added.")
            else:
                print("Could not add resource. Check ID uniqueness and total units.")

        elif choice == "2":
            _print_resources(manager.list_resources())

        elif choice == "3":
            fellow_id = input("Fellow ID: ").strip()
            resource_id = input("Resource ID: ").strip()
            quantity = _prompt_positive_int("Quantity: ")
            if quantity is None:
                continue
            if manager.borrow_resource(fellow_id, resource_id, quantity):
                print("Borrowing recorded.")
            else:
                print("Borrowing rejected. Check IDs and available units.")

        elif choice == "4":
            fellow_id = input("Fellow ID: ").strip()
            resource_id = input("Resource ID: ").strip()
            quantity = _prompt_positive_int("Quantity: ")
            if quantity is None:
                continue
            if manager.return_resource(fellow_id, resource_id, quantity):
                print("Return recorded.")
            else:
                print("Return rejected. Check outstanding loan quantity.")

        elif choice == "5":
            query = input("Name search query: ").strip()
            _print_resources(manager.search_by_name(query))

        elif choice == "6":
            category = input("Category: ").strip()
            _print_resources(manager.filter_by_category(category))

        elif choice == "7":
            report = manager.generate_report()
            print(f"Total units: {report['total_units']}")
            print(f"Available units: {report['available_units']}")
            print(f"Units currently borrowed: {report['units_borrowed']}")
            print("Resources with fewer than 3 available units:")
            _print_resources(report["low_stock_resources"])
            if report["most_borrowed_resources"]:
                print("Most borrowed resource(s):")
                _print_resources(report["most_borrowed_resources"])
            else:
                print("Most borrowed resource(s): none")

        elif choice == "8":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Please choose 1-8.")


if __name__ == "__main__":
    run_cli()
