import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js';
import { getFirestore, collection, query, where, getDocs } from 'https://www.gstatic.com/firebasejs/9.6.10/firebase-firestore.js';
    let firebaseConfig = {
        apiKey: "AIzaSyAM0wDc_WO0wP3-_TPRPLENZDIHbezH7U4",
        authDomain: "flutterapp-fd5c3.firebaseapp.com",
        projectId: "flutterapp-fd5c3"
    };

    const app = initializeApp(firebaseConfig);
    const db = getFirestore(app);
export async function fetchAllItems() {
    const itemsQuery1 = query(collection(db, "item"), where("quantity", ">", 0));

    // Second query: where pre_order is true
    const itemsQuery2 = query(collection(db, "item"), where("pre_order", "==", true));

    // Fetch both queries in parallel
    const [querySnapshot1, querySnapshot2] = await Promise.all([
        getDocs(itemsQuery1),
        getDocs(itemsQuery2)
    ]);

    // Get the data from both queries and combine the results
    const items1 = querySnapshot1.docs.map(doc => doc.data());
    const items2 = querySnapshot2.docs.map(doc => doc.data());

    return [...items1, ...items2];
}

export async function fetchFavouriteItems(userEmail) {
    const favouritesQuery = query(collection(db, "Favourites"), where("email", "==", userEmail));
    const querySnapshot = await getDocs(favouritesQuery);
    return querySnapshot.docs.map(doc => doc.data());
}

export async function fetchStones() {
    const stonesQuery = query(collection(db, "Stones")); // Запрос к коллекции Stones
    const querySnapshot = await getDocs(stonesQuery);

    // Convert documents into an object { “id”: “name” }
    let stones_reversed = {};
    const all_stones = {};
    querySnapshot.docs.forEach(doc => {
        const data = doc.data();
        if (data.id && data.name) { // Убедимся, что данные существуют
            all_stones[data.id] = data.name;
            stones_reversed[data.name] = data.id;
        }
    });

    return {"all": all_stones, "reversed": stones_reversed};
}

export async function fetchItemsWithQuantityGreaterThan30(elements) {
        const maxElementsPerQuery = 10;
        let items = [];

        for (let i = 0; i < elements.length; i += maxElementsPerQuery) {
            const chunk = elements.slice(i, i + maxElementsPerQuery);
            const itemsQuery = query(collection(db, "item"),
                where("quantity", ">", 30),
                where("name", "in", chunk)
            );
            const querySnapshot = await getDocs(itemsQuery);

            querySnapshot.forEach(doc => {
                items.push(doc.data());
            });
        }

        return items;
    }