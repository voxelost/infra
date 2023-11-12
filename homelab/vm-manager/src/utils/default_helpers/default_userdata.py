from models.cloud_init.userdata import UserData, User

def get_default_userdata() -> UserData:
    return UserData(
        users=[
            User(
                name='kim',
                lock_passwd=False,
                hashed_passwd='$1$x9fXkSPH$p1ffAhqDKAvT4Stz35l4C/', # passwd: 'possible' # <output from openssl passwd -1>
                ssh_authorized_keys=[
                    'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAD9QD3Ktvnq5P9oa4XxZ/h1tSAQnGdZkjAxCU0jlZ1UsWp9hf0/vRLlvHa6B6xaaaZZfaIuUkh3Y+y6obRbul+SZ1ru8ixj+KJkl0b0ZL20PJ0lbN3n8IiE1x53xCsXkjt0F7GHVmzUMuyguff0bnCd2Nf6O0u6ja0766NwJ5G565lBkZT7Q4u38+XZSFH4r9F9emWZxEF9EfteF8LqyLlCDAcrPDbe6iqhXqjUlTD6uNORMKh1i1U49yB6khNcy2rwJYuIFtd0KSqShhHBkWGdrsUnjN7KEEuc0ORvfryJDaEcIoqodXcYbHH2W0gE4DHl71n4l2/XKg5z1NzUWcxcJWSnmfwTkynVFqpdAm0hz+54andsya9exHbgWkqsoaZx/ecZNUySoIgnQGXp+yGUg6q0DwVDA4EdWhlmwSpJ+EU6tozzaxsRK7mZZTpC4sz/wnJNb5itjAS2vd3wxslPRliIyQFvNrNc5bGY9G4ECA6+CbVh8KexSNZD08udypiVO875TZM0WUbN+TmTtjfMAcdfYji0ZNRMv02nnMkll754KKe9BplzAjNYKy7ol3rb9/shA/aoihEi7pLhUEl6jjdT/el43MBzxSe5uJpCs/i3KYj8AcxKVqmcN1P9M5JOFqMNcT5lG3slMlfXGhZ6ZTPpSVFY2XF8GiXAvPMCfRxsZWpf3wlBNv+GKMlOOE098QKr7m97YIXsBCpDzrneZQTI5lI9tHrFDEU0I9A7qKjrnXV+j4JLXyLJ3hMUnyAgKNbNeV2rnQrRvw/3m9Svsmrn/ozWMdvc9uLUZHXojiQbGPwhy2Ycw0lheIv0F25sQSqS0UicVf63wNhy3NC7u11Pm2p9HO2qKpe2xvG5E/VS2v6Z8XErm4D3HWdoA20d4ljOU1UNTnP1HW04Xs0QjVs9CniX/1zdsNIHWV+wE74tjDVPyyF/kh4ptbf/Rt7FPksZe3eyd/YLGHf/lejo59zL+HRRkjsaA1CYzpg9NSzeSIX/MROwsV2pcRtboCnrX8L+PpbkDOor/ku96x2qj52gKi32atuKeYja+m6+3rDPbgl6XWTCUCcxfB9FZ/5JpHeCOFqKQE1O3KKODT3wrEaeWfWXWoawynwLnd/020i7oEUOBTX6z+ViONBzLkM71Boa3iVLToB/6AjbmFd3tv7KLxAqutP8emI2efrn0eDh3R0bZJ8oCy01d6jFEllIFYI/t7e8u/iPWbFKx8Shn7whgH0BFR8+KbvfCxLlmg7v4lpCEr7ucE9YZDydXaDGN37G3W5Gn3yt/0LApIh11gr+Zp82jIgdmGfhOErSop7/c/b0mndk4XCK2SICYbtLZ74FnRV',
                ],
                sudo=['ALL=(ALL) NOPASSWD:ALL'],
                groups='users, sudo',
                shell='/bin/bash'
            )
        ],
        package_update=True,
        package_upgrade=True,
        packages=['qemu-guest-agent'],
        runcmd=[
            'systemctl enable --now qemu-guest-agent.service'
        ]
    )
