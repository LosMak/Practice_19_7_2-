from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверка на возврат статус-кода 200 при запросе API ключа и содержание 'key' в result:"""
    status, result = pf.get_api_key(email, password)  # Отправляем запрос:
    assert status == 200                              # сохраняем полученный ответ с кодом статуса в status
    assert 'key' in result                            # сохраняем текст ответа 'key' в result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем API ключ и сохраняем в переменную auth_key.
        Далее используя этот ключ запрашиваем список всех питомцев и проверяем, что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pets_with_valid_data(name='Зайка',
                                      animal_type='Заяц',
                                      age='1',
                                      pet_photo='image/pet.jpg'):
    """Проверяем, возможность добавления новой карточки питомца с фото и корректными данными"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)  # Получаем полный путь изображения питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)       # Cохраняем в переменную pet_photo
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверка возможности удаления карточки питомца"""  # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового, повторно запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Зая", "Крол", "2", "images/pet.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Повторно запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем, что статус-код 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Пушистая',
                                         animal_type='Крольчиха',
                                         age=2):
    """Проверяем возможность обновления информации о питомце. Если список пуст, необходимо сначала добавить питомца"""
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем, что статус-код 200 и имя питомца соответствует указанному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выдаём исключение-сообщение об отсутствии своих питомцев
        raise Exception("Нет моих домашних животных")

# Тест 1


def test_add_new_pet_with_empty_values(name='',
                                       animal_type='',
                                       age='',
                                       pet_photo='image/pet.jpg'):
    """Проверяем, что можно добавить питомца с пустыми данным, кроме фото животного"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['pet_photo'] is not None

# Тест 2


def test_add_new_pet_without_photo(name='Зая',
                                   animal_type='Крол',
                                   age='3'):
    """Проверяем, что можно добавить питомца без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name

# Тест 3


def test_add_photo_to_existing_pet(pet_photo='image/pet.jpg'):
    """Проверяем возможность добавления фотографии питомца """
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_of_pet(api_key, my_pets['pets'][0]['id'], pet_photo)

        _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        raise Exception('Питомцы отсутствуют')

# Тест 4


def test_add_new_pet_with_negative_age(name='Зая',
                                       animal_type='Кролик',
                                       age='-1',
                                       pet_photo='image/pet.jpg'):
    """Проверяем можно ли добавить питомца с отрицательным возрастом - Баг"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['age'] == age

# Тест 5


def test_add_pet_with_exceeding_symbol_in_animal_type(name='Зая',
                                                      animal_type='Кроликоподобное',
                                                      age='1',
                                                      pet_photo='image/pet.jpg'):
    """Проверка на добавление питомца с вводом значения превышающим 12 знаков в поле "animal_type - Баг"""
    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    list_animal_type = result['animal_type'].split()
    symbol_count = len(list_animal_type)

    assert status == 200
    assert symbol_count <= 12, 'В приложение добавлен питомец с названием породы превышающим 12 символов.'

# Тест 6


def test_add_pet_with_four_digit_age(name='Зая',
                                     animal_type='Крол',
                                     age='9999',
                                     pet_photo='image/pet.jpg'):
    """Добавление питомца с вводом в поле 'age' более трёхзначного числа - Баг"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    count = result['age']
    assert status == 200
    assert len(count) <= 3

# Тест 7


def test_add_pet_with_centennial_age(name='Зая',
                                     animal_type='Енот',
                                     age='101',
                                     pet_photo='image/pet.jpg'):
    """Проверка возможности добавления питомца возрастом старше 100 лет.
       При попытке добавления питомца старше 100 лет, ожидается ошибка - Баг."""
    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(api_key, name, animal_type, age, pet_photo)

    age = result['age'].split()
    age_count = len(age)

    assert status == 200
    assert age_count <= 100, 'Добавлена карточка питомца с возрастом более 100 лет'

# Тест 8


def test_api_key_with_incorrect_password(email=valid_email, password=invalid_password):
    """Проверка на ввод валидного email c невалидным паролем.Проверка наличия ключа в результате"""
    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result

# Тест 9


def test_api_key_with_correct_password_valid_email(email=invalid_email, password=valid_password):
    """Проверка на ввод невалидного email c валидным паролем.Проверка наличия ключа в результате"""
    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result

# Тест 10


def test_api_key_with_incorrect_password_invalid_email(email=invalid_email, password=invalid_password):
    """Проверка на ввод невалидного email и невалидого пароля.Проверка наличия ключа в результате"""
    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result
