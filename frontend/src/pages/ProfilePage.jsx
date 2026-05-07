function ProfilePage() {
  return (
    <main className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold">Личный кабинет</h1>

      <section className="bg-white rounded-2xl border p-6 mt-6 shadow-sm">
        <h2 className="text-xl font-bold">Профиль пользователя</h2>
        <p className="text-slate-600 mt-3">Имя: Иван Петров</p>
        <p className="text-slate-600">Email: ivan@example.com</p>
      </section>

      <section className="bg-white rounded-2xl border p-6 mt-6 shadow-sm">
        <h2 className="text-xl font-bold">Мои бронирования</h2>
        <div className="mt-4 border rounded-2xl p-5">
          <h3 className="font-semibold">Grand Hotel Neva</h3>
          <p className="text-slate-600">Стандартный номер · 2 гостя</p>
          <p className="text-slate-600">Статус: подтверждено</p>
        </div>
      </section>
    </main>
  );
}

export default ProfilePage;
